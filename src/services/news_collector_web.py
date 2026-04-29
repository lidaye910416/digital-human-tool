"""
固定网站新闻采集器

实现 BaseCollector 接口，从没有 RSS 的固定网站采集新闻

依赖安装: pip install beautifulsoup4 playwright
"""

import re
import httpx
import logging
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from src.services.news_collector_base import BaseCollector
from src.models.news_bilingual import NewsItem

logger = logging.getLogger(__name__)


class WebParser(ABC):
    """
    网站解析器抽象基类
    
    每个需要爬取的网站需要实现自己的解析器
    """
    
    name: str = "base"
    
    @abstractmethod
    async def parse_list(self, html: str) -> List[Dict]:
        """
        解析列表页
        
        Returns:
            List[Dict]: 每项包含 title, url, summary 等
        """
        pass
    
    @abstractmethod
    async def parse_detail(self, html: str, url: str) -> Dict:
        """
        解析详情页
        
        Returns:
            Dict: 包含 title, content 等
        """
        pass


class DefaultWebParser(WebParser):
    """默认网页解析器（使用正则）"""
    
    name = "default"
    
    def __init__(self, selectors: Dict = None):
        """
        Args:
            selectors: CSS 选择器配置
                - list: 列表项选择器
                - title: 标题选择器
                - link: 链接选择器
                - summary: 摘要选择器
        """
        self.selectors = selectors or {}
    
    async def parse_list(self, html: str) -> List[Dict]:
        """解析列表页（基础实现）"""
        # 这里可以使用 BeautifulSoup，但基础版本返回空
        # 实际使用时应该继承并实现具体的解析逻辑
        return []
    
    async def parse_detail(self, html: str, url: str) -> Dict:
        """解析详情页"""
        # 清理 HTML 获取纯文本
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return {
            "content": text[:5000],  # 限制长度
            "title": "",
            "summary": text[:300]
        }


class WebCollector(BaseCollector):
    """
    固定网站采集器
    
    从没有 RSS 的网站采集新闻
    """
    
    type = "web"
    MAX_PAGES = 3  # 最多爬取页数
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.start_url = config.get("url", "")
        self.selectors = config.get("selectors", {})
        self.pagination = config.get("pagination", {})
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 创建解析器
        parser_name = config.get("parser", "default")
        self.parser = self._create_parser(parser_name)
    
    def _create_parser(self, parser_name: str) -> WebParser:
        """创建解析器"""
        # 可以扩展支持不同的解析器
        # 目前只支持默认解析器
        return DefaultWebParser(self.selectors)
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
    
    async def collect(self) -> List[NewsItem]:
        """从固定网站采集新闻"""
        if not self.enabled:
            return []
        
        if not self.start_url:
            logger.warning(f"WebCollector {self.name}: No URL configured")
            return []
        
        try:
            items = []
            
            # 获取列表页
            response = await self.client.get(self.start_url)
            response.raise_for_status()
            
            list_items = await self.parser.parse_list(response.text)
            
            # 解析每个条目
            for item in list_items[:self.MAX_PAGES * 10]:  # 每页限制
                url = item.get('url')
                if not url:
                    continue
                
                # 获取详情页
                detail = await self._fetch_detail(url)
                if detail:
                    news = self.create_news_item(
                        title=item.get('title', ''),
                        content=detail.get('content', ''),
                        summary=detail.get('summary', item.get('summary', '')),
                        source_name=self.name,
                        source_url=url,
                        published_at=item.get('published', '')
                    )
                    if news.title_zh or news.title_en:
                        items.append(news)
            
            logger.info(f"WebCollector {self.name}: Collected {len(items)} items")
            return items
            
        except Exception as e:
            logger.warning(f"WebCollector {self.name}: {e}")
            return []
    
    async def _fetch_detail(self, url: str) -> Optional[Dict]:
        """获取详情页"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return await self.parser.parse_detail(response.text, url)
        except Exception as e:
            logger.warning(f"Failed to fetch detail {url}: {e}")
            return None
    
    def __repr__(self):
        return f"<WebCollector name={self.name} url={self.start_url}>"


class BilingualWebCollector:
    """
    双语网站采集器
    
    管理多个固定网站采集器
    """
    
    def __init__(self, sites: List[Dict] = None):
        from src.config.sources import WEB_SITES
        
        self.sites = sites or [s for s in WEB_SITES if s.get("enabled", False)]
        self.collectors = [WebCollector(s) for s in self.sites]
    
    async def collect_all(self, lang: Optional[str] = None) -> List[NewsItem]:
        """收集所有/指定语言的新闻"""
        items = []
        for collector in self.collectors:
            if lang is None or collector.language == lang:
                items.extend(await collector.collect())
        return items
    
    async def close(self):
        """关闭所有采集器"""
        for collector in self.collectors:
            await collector.close()
