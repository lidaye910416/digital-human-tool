"""
统一新闻采集调度器

整合 RSS、网站爬取、API 三种采集方式
"""

import re
import logging
from typing import List, Dict, Optional
from datetime import datetime

from src.models.news_bilingual import NewsItem
from src.services.news_collector_rss import BilingualRSSCollector
from src.services.news_collector_web import BilingualWebCollector
from src.services.news_collector_api import BilingualAPICollector

logger = logging.getLogger(__name__)


class NewsCollector:
    """
    统一新闻采集调度器
    
    使用策略:
    1. RSS 采集器 (主要)
    2. 固定网站爬取器 (补充)
    3. API 数据源 (可选)
    
    示例:
        collector = NewsCollector()
        items = await collector.collect(lang='zh', min_quality=55)
    """
    
    def __init__(
        self,
        rss_enabled: bool = True,
        web_enabled: bool = False,
        api_enabled: bool = False
    ):
        """
        Args:
            rss_enabled: 启用 RSS 采集
            web_enabled: 启用网站爬取
            api_enabled: 启用 API 采集
        """
        # 创建各类型采集器
        self.rss_collector = BilingualRSSCollector() if rss_enabled else None
        self.web_collector = BilingualWebCollector() if web_enabled else None
        self.api_collector = BilingualAPICollector() if api_enabled else None
        
        logger.info(f"NewsCollector initialized: RSS={rss_enabled}, Web={web_enabled}, API={api_enabled}")
    
    async def collect(
        self,
        lang: Optional[str] = None,
        category: Optional[str] = None,
        min_quality: float = 0
    ) -> List[NewsItem]:
        """
        收集新闻
        
        Args:
            lang: 语言过滤 (zh/en/None=全部)
            category: 分类过滤 (ai/tools/news/product/None=全部)
            min_quality: 最低质量分数
            
        Returns:
            List[NewsItem]: 收集到的新闻列表
        """
        items = []
        
        # RSS 采集
        if self.rss_collector:
            rss_items = await self.rss_collector.collect_all(lang)
            items.extend(rss_items)
            logger.info(f"RSS collected: {len(rss_items)} items")
        
        # 网站爬取
        if self.web_collector:
            web_items = await self.web_collector.collect_all(lang)
            items.extend(web_items)
            logger.info(f"Web collected: {len(web_items)} items")
        
        # API 采集
        if self.api_collector:
            api_items = await self.api_collector.collect_all(lang)
            items.extend(api_items)
            logger.info(f"API collected: {len(api_items)} items")
        
        # 去重
        items = self._deduplicate(items)
        logger.info(f"After deduplication: {len(items)} items")
        
        # 分类过滤
        if category:
            items = [n for n in items if n.category == category]
            logger.info(f"After category filter ({category}): {len(items)} items")
        
        # 质量过滤
        if min_quality > 0:
            items = [n for n in items if (n.quality.total_100 if n.quality else 0) >= min_quality]
            logger.info(f"After quality filter (>={min_quality}): {len(items)} items")
        
        # 按质量排序
        items.sort(key=lambda x: x.quality.total_100 if x.quality else 0, reverse=True)
        
        return items
    
    def _deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """去重"""
        seen_titles = set()
        unique_items = []
        
        for item in items:
            norm_title = re.sub(r'[^一-龥a-zA-Z0-9]', '', item.title_zh or item.title_en)
            norm_title = norm_title.lower()[:30]
            
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique_items.append(item)
        
        return unique_items
    
    async def collect_zh(self, **kwargs) -> List[NewsItem]:
        """收集中文新闻"""
        return await self.collect(lang='zh', **kwargs)
    
    async def collect_en(self, **kwargs) -> List[NewsItem]:
        """收集英文新闻"""
        return await self.collect(lang='en', **kwargs)
    
    async def collect_all(self, **kwargs) -> List[NewsItem]:
        """收集所有新闻"""
        return await self.collect(lang=None, **kwargs)
    
    async def close(self):
        """关闭所有采集器"""
        if self.rss_collector:
            await self.rss_collector.close()
        if self.web_collector:
            await self.web_collector.close()
        if self.api_collector:
            await self.api_collector.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ===== 便捷函数 =====

async def collect_news(
    lang: Optional[str] = None,
    category: Optional[str] = None,
    min_quality: float = 55,
    rss_only: bool = True
) -> List[NewsItem]:
    """
    便捷函数: 收集新闻

    Args:
        lang: 语言 (zh/en/None=全部)
        category: 分类 (ai/tools/news/product/None=全部)
        min_quality: 最低质量分数
        rss_only: 只使用 RSS 采集

    Returns:
        List[NewsItem]: 新闻列表
    """
    async with NewsCollector(rss_enabled=True, web_enabled=not rss_only, api_enabled=False) as collector:
        return await collector.collect(lang=lang, category=category, min_quality=min_quality)


# ===== 向后兼容 =====
# news_collector 实例已移除，统一使用 NewsCollector 类或 collect_news 函数
