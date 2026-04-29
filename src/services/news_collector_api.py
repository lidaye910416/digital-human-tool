"""
API 数据源采集器

实现 BaseCollector 接口，从 API 接口获取新闻数据
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

import httpx

from src.services.news_collector_base import BaseCollector
from src.models.news_bilingual import NewsItem

logger = logging.getLogger(__name__)


class APICollector(BaseCollector):
    """
    API 数据源采集器
    
    从 REST API 获取新闻数据
    """
    
    type = "api"
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_url = config.get("url", "")
        self.headers = config.get("headers", {})
        self.mapping = config.get("mapping", {})
        self.params = config.get("params", {})
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
    
    async def collect(self) -> List[NewsItem]:
        """从 API 获取新闻"""
        if not self.enabled:
            return []
        
        if not self.api_url:
            logger.warning(f"APICollector {self.name}: No URL configured")
            return []
        
        try:
            response = await self.client.get(
                self.api_url,
                headers=self.headers,
                params=self.params
            )
            response.raise_for_status()
            
            data = response.json()
            items = self._parse_response(data)
            
            logger.info(f"APICollector {self.name}: Collected {len(items)} items")
            return items
            
        except httpx.HTTPError as e:
            logger.warning(f"APICollector {self.name}: HTTP error - {e}")
            return []
        except Exception as e:
            logger.warning(f"APICollector {self.name}: {e}")
            return []
    
    def _parse_response(self, data) -> List[NewsItem]:
        """解析 API 响应"""
        items = []
        
        # 支持数组或包含数组的响应
        if isinstance(data, list):
            raw_items = data
        elif isinstance(data, dict):
            # 尝试常见的数据路径
            raw_items = data.get('data', data.get('items', data.get('news', [])))
        else:
            raw_items = []
        
        for raw in raw_items:
            news = self._map_item(raw)
            if news:
                items.append(news)
        
        return items
    
    def _map_item(self, raw: Dict) -> Optional[NewsItem]:
        """将 API 响应映射到 NewsItem"""
        try:
            # 根据 mapping 配置映射字段
            title = raw.get(self.mapping.get('title', 'title'), '')
            content = raw.get(self.mapping.get('content', 'content'), '')
            summary = raw.get(self.mapping.get('summary', 'summary'), '')
            url = raw.get(self.mapping.get('url', 'url') or self.mapping.get('link', 'link'), '')
            published = raw.get(self.mapping.get('published_at', 'publishedAt') or self.mapping.get('published', 'published'), '')
            
            if not title:
                return None
            
            return self.create_news_item(
                title=title,
                content=content,
                summary=summary or content[:300],
                source_name=self.name,
                source_url=url,
                published_at=published
            )
            
        except Exception as e:
            logger.warning(f"Failed to map item: {e}")
            return None
    
    def __repr__(self):
        return f"<APICollector name={self.name} url={self.api_url}>"


class BilingualAPICollector:
    """
    双语 API 采集器
    
    管理多个 API 数据源
    """
    
    def __init__(self, sources: List[Dict] = None):
        from src.config.sources import API_SOURCES
        
        self.sources = sources or [s for s in API_SOURCES if s.get("enabled", False)]
        self.collectors = [APICollector(s) for s in self.sources]
    
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
