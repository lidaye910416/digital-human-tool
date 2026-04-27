"""科技资讯收集服务

参考 tech-news-digest 的收集逻辑
支持: RSS、GitHub Trending、Web搜索
"""
import feedparser
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.models.news import NewsItem

logger = logging.getLogger(__name__)

class NewsCollector:
    """资讯收集器"""
    
    # 默认 RSS 源
    DEFAULT_RSS_SOURCES = [
        {
            "name": "Hacker News",
            "url": "https://hnrss.org/frontpage",
            "category": "tech"
        },
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com/feed/",
            "category": "tech"
        },
        {
            "name": "AI News",
            "url": "https://www.artificialintelligence-news.com/feed/",
            "category": "ai"
        },
        {
            "name": "MIT Technology Review",
            "url": "https://www.technologyreview.com/feed/",
            "category": "tech"
        },
    ]
    
    # GitHub Trending 话题
    GITHUB_TOPICS = ["llm", "ai-agent", "open-source-ai", "machine-learning"]
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def collect_all(self, db: Session, target_date: str = None) -> Dict[str, int]:
        """收集所有来源的资讯
        
        Args:
            db: 数据库会话
            target_date: 目标日期，默认为昨日
        """
        if target_date is None:
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        logger.info(f"Starting news collection for date: {target_date}")
        
        stats = {
            "rss": 0,
            "github": 0,
            "total": 0
        }
        
        # 1. 收集 RSS
        stats["rss"] = await self._collect_rss(db, target_date)
        
        # 2. 收集 GitHub Trending
        stats["github"] = await self._collect_github(db, target_date)
        
        stats["total"] = stats["rss"] + stats["github"]
        logger.info(f"Collection complete: {stats}")
        
        return stats
    
    async def _collect_rss(self, db: Session, target_date: str) -> int:
        """收集 RSS 源"""
        count = 0
        
        for source in self.DEFAULT_RSS_SOURCES:
            try:
                logger.info(f"Fetching RSS: {source['name']}")
                items = await self._fetch_rss(source["url"])
                
                for item in items:
                    # 检查日期是否符合目标日期
                    if self._is_target_date(item.get("published"), target_date):
                        news = NewsItem(
                            title=self._clean_text(item.get("title", "")),
                            summary=self._clean_text(item.get("summary", "")),
                            content=self._clean_text(item.get("content", item.get("summary", ""))),
                            source_url=item.get("link", ""),
                            source_name=source["name"],
                            category=source["category"],
                            published_at=self._parse_date(item.get("published")),
                            date_key=target_date,
                            score=self._calculate_score(item)
                        )
                        db.add(news)
                        count += 1
                
            except Exception as e:
                logger.error(f"RSS collection failed for {source['name']}: {e}")
        
        db.commit()
        return count
    
    async def _fetch_rss(self, url: str) -> List[Dict]:
        """获取 RSS 内容"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            items = []
            
            for entry in feed.entries[:20]:  # 限制数量
                items.append({
                    "title": getattr(entry, "title", ""),
                    "summary": getattr(entry, "summary", ""),
                    "content": getattr(entry, "content", [{}])[0].get("value", "") if hasattr(entry, "content") else "",
                    "link": getattr(entry, "link", ""),
                    "published": getattr(entry, "published", None)
                })
            
            return items
        except Exception as e:
            logger.error(f"RSS fetch failed: {url} - {e}")
            return []
    
    async def _collect_github(self, db: Session, target_date: str) -> int:
        """收集 GitHub Trending"""
        count = 0
        
        try:
            # 获取 GitHub Trending
            response = await self.client.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": " ".join(self.GITHUB_TOPICS),
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 10
                },
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for repo in data.get("items", [])[:10]:
                    # 检查是否是新仓库（昨天创建或最近活跃）
                    created = repo.get("created_at", "")
                    pushed = repo.get("pushed_at", "")
                    
                    news = NewsItem(
                        title=f"🔥 {repo['full_name']}: {repo.get('description', 'No description')}",
                        summary=repo.get("description", ""),
                        content=f"⭐ Stars: {repo.get('stargazers_count', 0)}\n🍴 Forks: {repo.get('forks_count', 0)}\n📝 Language: {repo.get('language', 'Unknown')}",
                        source_url=repo.get("html_url", ""),
                        source_name="GitHub Trending",
                        category="tech",
                        published_at=self._parse_date(created),
                        date_key=target_date,
                        score=min(repo.get("stargazers_count", 0) / 100, 10)
                    )
                    db.add(news)
                    count += 1
                
        except Exception as e:
            logger.error(f"GitHub collection failed: {e}")
        
        db.commit()
        return count
    
    def _is_target_date(self, published_str: str, target_date: str) -> bool:
        """检查发布日期是否符合目标日期"""
        if not published_str:
            return True  # 无日期信息时默认收集
        
        try:
            dt = self._parse_date(published_str)
            if dt:
                return dt.strftime("%Y-%m-%d") == target_date
        except:
            pass
        
        return True  # 解析失败时默认收集
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return None
        
        from email.utils import parsedate_to_datetime
        
        try:
            return parsedate_to_datetime(date_str)
        except:
            pass
        
        # 尝试常用格式
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S+00:00",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str[:19], fmt)
            except:
                pass
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本，移除 HTML 标签"""
        if not text:
            return ""
        
        import re
        
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 解码 HTML 实体
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        return text.strip()
    
    def _calculate_score(self, item: Dict) -> float:
        """计算资讯评分"""
        score = 5.0  # 基础分
        
        title = item.get("title", "")
        
        # 关键词加分
        keywords = ["AI", "LLM", "GPT", "OpenAI", "Google", "Microsoft", "Meta", "Apple"]
        for kw in keywords:
            if kw.lower() in title.lower():
                score += 1
        
        return min(score, 10.0)
    
    async def close(self):
        await self.client.aclose()


# 全局实例
news_collector = NewsCollector()
