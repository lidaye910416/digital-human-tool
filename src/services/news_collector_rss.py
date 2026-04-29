"""
RSS 新闻采集器

实现 BaseCollector 接口，从 RSS 源采集新闻
"""

import re
import httpx
import feedparser
import logging
from typing import List, Dict, Optional

from src.services.news_collector_base import BaseCollector
from src.models.news_bilingual import NewsItem

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    """
    RSS 采集器
    
    从 RSS/Atom 订阅源采集新闻
    """
    
    type = "rss"
    MAX_ITEMS_PER_SOURCE = 10  # 每个源最多采集条数
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.url = config.get("url", "")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
    
    async def collect(self) -> List[NewsItem]:
        """从 RSS 源采集新闻"""
        if not self.enabled:
            return []
        
        if not self.url:
            logger.warning(f"RSSCollector {self.name}: No URL configured")
            return []
        
        try:
            response = await self.client.get(self.url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            
            items = []
            for entry in feed.entries[:self.MAX_ITEMS_PER_SOURCE]:
                news = self._parse_entry(entry)
                if news:
                    items.append(news)
            
            logger.info(f"RSSCollector {self.name}: Collected {len(items)} items")
            return items
            
        except httpx.TimeoutException:
            logger.warning(f"RSSCollector {self.name}: Timeout")
            return []
        except httpx.HTTPError as e:
            logger.warning(f"RSSCollector {self.name}: HTTP error - {e}")
            return []
        except Exception as e:
            logger.warning(f"RSSCollector {self.name}: {e}")
            return []
    
    def _parse_entry(self, entry) -> Optional[NewsItem]:
        """解析 RSS 条目"""
        # 获取内容
        content = ""
        if hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        elif hasattr(entry, 'content'):
            content = entry.content[0].value if entry.content else ""
        
        # 清理 HTML
        content = self._clean_html(content)
        
        # 获取标题
        title = entry.get('title', '')[:200]
        if not title:
            return None
        
        # 生成摘要
        summary = content[:300] if content else ""
        
        # 创建新闻条目
        return self.create_news_item(
            title=title,
            content=content,
            summary=summary,
            source_name=self.name,
            source_url=entry.get('link', ''),
            published_at=entry.get('published', '')
        )
    
    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签"""
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def __repr__(self):
        return f"<RSSCollector name={self.name} url={self.url}>"


class BilingualRSSCollector:
    """
    双语 RSS 采集器
    
    同时管理中文和英文 RSS 采集器
    """
    
    def __init__(self, zh_sources: List[Dict] = None, en_sources: List[Dict] = None):
        from src.config.sources import RSS_SOURCES_ZH, RSS_SOURCES_EN
        
        self.zh_sources = zh_sources or RSS_SOURCES_ZH
        self.en_sources = en_sources or RSS_SOURCES_EN
        
        # 创建采集器
        self.zh_collectors = [RSSCollector(s) for s in self.zh_sources]
        self.en_collectors = [RSSCollector(s) for s in self.en_sources]
    
    async def collect_zh(self) -> List[NewsItem]:
        """收集中文新闻"""
        items = []
        for collector in self.zh_collectors:
            items.extend(await collector.collect())
        return items
    
    async def collect_en(self) -> List[NewsItem]:
        """收集英文新闻"""
        items = []
        for collector in self.en_collectors:
            items.extend(await collector.collect())
        return items
    
    async def collect_all(self, lang: Optional[str] = None) -> List[NewsItem]:
        """收集所有/指定语言的新闻"""
        if lang == 'zh':
            return await self.collect_zh()
        elif lang == 'en':
            return await self.collect_en()
        else:
            zh_items = await self.collect_zh()
            en_items = await self.collect_en()
            return zh_items + en_items
    
    async def close(self):
        """关闭所有采集器"""
        for collector in self.zh_collectors + self.en_collectors:
            await collector.close()
    
    @staticmethod
    def deduplicate(items: List[NewsItem]) -> List[NewsItem]:
        """去重"""
        seen_titles = set()
        unique_items = []
        
        for item in items:
            # 标准化标题
            norm_title = re.sub(r'[^一-龥a-zA-Z0-9]', '', item.title_zh or item.title_en)
            norm_title = norm_title.lower()[:30]
            
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique_items.append(item)
        
        return unique_items
