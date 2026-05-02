"""
新闻数据获取层 - 解耦 RSS/Web/API 获取逻辑

职责: 只负责从各种来源获取原始数据，不做解析
"""

import feedparser
import httpx
import logging
from typing import List, Dict, Optional, AsyncIterator
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """获取器基类"""
    
    @abstractmethod
    async def fetch(self) -> List[Dict]:
        """获取原始数据列表"""
        pass
    
    @abstractmethod
    async def fetch_one(self, url: str) -> Optional[Dict]:
        """获取单个条目"""
        pass


class RSSFetcher(BaseFetcher):
    """RSS Feed 获取器"""
    
    def __init__(self, limit_per_source: int = 10):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.limit_per_source = limit_per_source
    
    async def close(self):
        await self.client.aclose()
    
    async def fetch_sources(self, sources: List[Dict]) -> List[Dict]:
        """从多个RSS源获取数据"""
        items = []
        for source in sources:
            try:
                entries = await self.fetch(source['url'])
                for entry in entries:
                    entry['_source'] = source
                items.extend(entries)
            except Exception as e:
                logger.warning(f"Failed to fetch {source.get('name', 'unknown')}: {e}")
        return items
    
    async def fetch(self, url: str) -> List[Dict]:
        """获取单个RSS源"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            
            entries = []
            for entry in feed.entries[:self.limit_per_source]:
                # 统一转换为字典格式
                entries.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': self._get_content(entry),
                    'author': entry.get('author', ''),
                })
            return entries
        except Exception as e:
            logger.warning(f"RSS fetch failed for {url}: {e}")
            return []
    
    async def fetch_one(self, url: str) -> Optional[Dict]:
        """获取单个条目（详情页）"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            if feed.entries:
                entry = feed.entries[0]
                return {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': self._get_content(entry),
                    'author': entry.get('author', ''),
                }
        except Exception as e:
            logger.warning(f"RSS fetch_one failed for {url}: {e}")
        return None
    
    def _get_content(self, entry) -> str:
        """获取条目内容"""
        if hasattr(entry, 'summary'):
            return entry.summary
        elif hasattr(entry, 'description'):
            return entry.description
        elif hasattr(entry, 'content'):
            return entry.content[0].value if entry.content else ""
        return ""


class WebFetcher(BaseFetcher):
    """网页爬取获取器 (预留接口)"""
    
    def __init__(self, selectors: Optional[Dict] = None):
        self.selectors = selectors or {}
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def fetch(self) -> List[Dict]:
        """网页爬取 (待实现)"""
        # TODO: 实现网页爬取逻辑
        logger.info("WebFetcher.fetch() - not implemented yet")
        return []
    
    async def fetch_one(self, url: str) -> Optional[Dict]:
        """爬取单个页面 (待实现)"""
        logger.info(f"WebFetcher.fetch_one({url}) - not implemented yet")
        return None


class APIFetcher(BaseFetcher):
    """API 获取器 (预留接口)"""
    
    def __init__(self, headers: Optional[Dict] = None):
        self.headers = headers or {}
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def fetch(self) -> List[Dict]:
        """API获取 (待实现)"""
        logger.info("APIFetcher.fetch() - not implemented yet")
        return []
    
    async def fetch_one(self, url: str) -> Optional[Dict]:
        """API单条获取 (待实现)"""
        logger.info(f"APIFetcher.fetch_one({url}) - not implemented yet")
        return None


def create_fetcher(source_type: str = 'rss') -> BaseFetcher:
    """工厂方法创建获取器"""
    if source_type == 'rss':
        return RSSFetcher()
    elif source_type == 'web':
        return WebFetcher()
    elif source_type == 'api':
        return APIFetcher()
    else:
        raise ValueError(f"Unknown fetcher type: {source_type}")
