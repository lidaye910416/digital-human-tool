"""
新闻采集器抽象基类

定义统一的采集器接口，确保各采集器之间解耦
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from src.models.news_bilingual import NewsItem, QualityScore


@dataclass
class CollectorConfig:
    """采集器配置"""
    name: str
    url: str
    category: str
    weight: float
    language: str
    enabled: bool = True


class BaseCollector(ABC):
    """
    采集器抽象基类
    
    所有采集器必须实现 collect() 方法
    """
    
    type: str = "base"  # 采集器类型: rss, web, api
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = config.get("name", "Unknown")
        self.category = config.get("category", "news")
        self.weight = config.get("weight", 1.0)
        self.language = config.get("language", "zh")
        self.enabled = config.get("enabled", True)
        
        self._analyzer = None
    
    @abstractmethod
    async def collect(self) -> List[NewsItem]:
        """
        采集新闻
        
        Returns:
            List[NewsItem]: 采集到的新闻列表
        """
        pass
    
    def create_news_item(
        self,
        title: str,
        content: str,
        summary: str,
        source_name: str,
        source_url: str,
        published_at: str = "",
        lang: Optional[str] = None
    ) -> NewsItem:
        """创建新闻条目"""
        language = lang or self.language
        
        news = NewsItem(
            title_zh=title if language == "zh" else "",
            title_en=title if language == "en" else "",
            content_zh=content if language == "zh" else "",
            content_en=content if language == "en" else "",
            summary_zh=summary if language == "zh" else "",
            summary_en=summary if language == "en" else "",
            source_zh=source_name if language == "zh" else "",
            source_en=source_name if language == "en" else "",
            source_url=source_url,
            lang=language,
            category=self.category,
            published_at=published_at or datetime.now().isoformat(),
            created_at=datetime.now().isoformat(),
            weight=self.weight
        )
        
        # 计算质量评分
        self._analyze_quality(news)
        
        return news
    
    def _analyze_quality(self, news: NewsItem):
        """分析新闻质量"""
        from src.services.news_collector_quality import NewsQualityAnalyzer
        
        if self._analyzer is None:
            self._analyzer = NewsQualityAnalyzer()
        
        title = news.title_zh or news.title_en
        summary = news.summary_zh or news.summary_en
        source = news.source_zh or news.source_en
        
        quality_dict = self._analyzer.analyze_quality(title, summary, source, news.source_url)
        
        news.quality = QualityScore(
            total_100=quality_dict.get('total_100', 0),
            weighted_total=quality_dict.get('weighted_total', 0),
            grade=quality_dict.get('grade', 'D'),
            scores=quality_dict.get('scores', {}),
            issues=quality_dict.get('issues', [])
        )
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} type={self.type}>"
