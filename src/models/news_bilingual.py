"""双语新闻数据模型"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid

@dataclass
class QualityScore:
    """质量评分"""
    total_100: float = 0.0          # 综合分数 0-100
    weighted_total: float = 0.0      # 加权总分 0-10
    grade: str = "D"                 # A+, A, B, C, D
    scores: Dict[str, float] = field(default_factory=dict)  # 各维度分数
    issues: List[str] = field(default_factory=list)  # 问题列表
    
    def to_dict(self) -> Dict:
        return {
            "total_100": self.total_100,
            "weighted_total": self.weighted_total,
            "grade": self.grade,
            "scores": self.scores,
            "issues": self.issues
        }

@dataclass
class NewsItem:
    """双语新闻条目"""
    # ID
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 标题
    title_zh: str = ""              # 中文标题
    title_en: str = ""              # 英文标题
    
    # 内容
    content_zh: str = ""            # 中文内容
    content_en: str = ""            # 英文内容
    
    # 摘要
    summary_zh: str = ""             # 中文摘要 (50-100字)
    summary_en: str = ""             # 英文摘要
    
    # 来源
    source_zh: str = ""              # 中文来源
    source_en: str = ""              # 英文来源
    source_url: str = ""             # 原文链接
    
    # 元数据
    lang: str = "both"               # 'zh' | 'en' | 'both'
    category: str = "news"          # 'ai' | 'tools' | 'news' | 'product'
    published_at: str = ""           # 发布时间
    created_at: str = ""             # 入库时间
    
    # 质量评分
    quality: QualityScore = field(default_factory=QualityScore)
    
    # 权重
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title_zh": self.title_zh,
            "title_en": self.title_en,
            "content_zh": self.content_zh,
            "content_en": self.content_en,
            "summary_zh": self.summary_zh,
            "summary_en": self.summary_en,
            "source_zh": self.source_zh,
            "source_en": self.source_en,
            "source_url": self.source_url,
            "lang": self.lang,
            "category": self.category,
            "published_at": self.published_at,
            "created_at": self.created_at,
            "quality": self.quality.to_dict() if isinstance(self.quality, QualityScore) else self.quality,
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NewsItem':
        """从字典创建"""
        quality_data = data.get('quality', {})
        quality = QualityScore(
            total_100=quality_data.get('total_100', 0),
            weighted_total=quality_data.get('weighted_total', 0),
            grade=quality_data.get('grade', 'D'),
            scores=quality_data.get('scores', {}),
            issues=quality_data.get('issues', [])
        )
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title_zh=data.get('title_zh', ''),
            title_en=data.get('title_en', ''),
            content_zh=data.get('content_zh', ''),
            content_en=data.get('content_en', ''),
            summary_zh=data.get('summary_zh', ''),
            summary_en=data.get('summary_en', ''),
            source_zh=data.get('source_zh', ''),
            source_en=data.get('source_en', ''),
            source_url=data.get('source_url', ''),
            lang=data.get('lang', 'both'),
            category=data.get('category', 'news'),
            published_at=data.get('published_at', ''),
            created_at=data.get('created_at', ''),
            quality=quality,
            weight=data.get('weight', 1.0)
        )
    
    def get_display(self, lang: str = 'zh') -> Dict[str, str]:
        """获取指定语言的显示内容"""
        if lang == 'zh':
            return {
                'title': self.title_zh or self.title_en,
                'content': self.content_zh or self.content_en,
                'summary': self.summary_zh or self.summary_en,
                'source': self.source_zh or self.source_en
            }
        elif lang == 'en':
            return {
                'title': self.title_en or self.title_zh,
                'content': self.content_en or self.content_zh,
                'summary': self.summary_en or self.summary_zh,
                'source': self.source_en or self.source_zh
            }
        else:  # both
            return {
                'title_zh': self.title_zh,
                'title_en': self.title_en,
                'content_zh': self.content_zh,
                'content_en': self.content_en,
                'summary_zh': self.summary_zh,
                'summary_en': self.summary_en,
                'source_zh': self.source_zh,
                'source_en': self.source_en
            }


@dataclass
class NewsCollection:
    """新闻集合"""
    items: List[NewsItem] = field(default_factory=list)
    last_update: str = ""
    total_count: int = 0
    quality_stats: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "items": [item.to_dict() for item in self.items],
            "last_update": self.last_update,
            "total_count": self.total_count,
            "quality_stats": self.quality_stats
        }
