"""
新闻收集流水线 - 整合各层组件

职责: 协调 fetcher, parser, scorer，完成端到端收集流程
"""

import logging
from typing import List, Optional
from src.config.sources import get_sources
from src.services.news_fetcher import RSSFetcher, create_fetcher
from src.services.news_parser import NewsParser
from src.services.news_scorer import NewsScorer

logger = logging.getLogger(__name__)


class NewsPipeline:
    """
    新闻收集流水线
    
    流程: Fetch → Parse → Score → Output
    """
    
    def __init__(self):
        self.fetcher = RSSFetcher()
        self.parser = NewsParser()
        self.scorer = NewsScorer()
    
    async def close(self):
        await self.fetcher.close()
    
    async def collect(
        self,
        lang: Optional[str] = None,
        category: Optional[str] = None,
        min_quality: float = 0
    ) -> List:
        """
        执行收集流程
        
        Args:
            lang: 语言筛选 'zh' | 'en' | None(全部)
            category: 分类筛选 'ai' | 'news' | 'tools' | 'product' | None
            min_quality: 最低质量分
        
        Returns:
            NewsItem 列表
        """
        # 1. 获取源配置
        sources = get_sources(language=lang)
        
        # 2. 获取原始数据
        raw_items = await self.fetcher.fetch_sources(sources)
        logger.info(f"Fetched {len(raw_items)} raw items")
        
        # 3. 解析为 NewsItem
        news_items = []
        for raw in raw_items:
            source_lang = raw.get('_source', {}).get('language', 'zh')
            item = self.parser.parse(raw, lang=source_lang)
            if item:
                news_items.append(item)
        
        logger.info(f"Parsed {len(news_items)} news items")
        
        # 4. 去重
        news_items = self.parser.deduplicate(news_items)
        logger.info(f"After deduplication: {len(news_items)} items")
        
        # 5. 质量评分
        news_items = self.scorer.score_batch(news_items)
        
        # 6. 过滤
        if category:
            news_items = [n for n in news_items if n.category == category]
        if min_quality > 0:
            news_items = [n for n in news_items if n.quality.total_100 >= min_quality]
        
        logger.info(f"Final: {len(news_items)} items")
        return news_items
    
    async def collect_single_source(self, source: dict) -> List:
        """从单个源收集"""
        raw_items = await self.fetcher.fetch_sources([source])
        
        news_items = []
        for raw in raw_items:
            item = self.parser.parse(raw, lang=source.get('language', 'zh'))
            if item:
                news_items.append(item)
        
        return self.scorer.score_batch(news_items)


# 全局实例
pipeline = NewsPipeline()
