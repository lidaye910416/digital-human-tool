"""科技资讯数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.sql import func
from src.models.database import Base

class NewsItem(Base):
    """科技资讯表"""
    __tablename__ = "news_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    title = Column(String(500), nullable=False, comment="资讯标题")
    summary = Column(Text, nullable=True, comment="资讯摘要")
    content = Column(Text, nullable=True, comment="完整内容")
    source_url = Column(String(1000), nullable=True, comment="来源链接")
    source_name = Column(String(100), nullable=False, comment="来源名称")
    
    # 分类
    category = Column(String(50), default="tech", comment="分类: tech/ai/crypto/web3")
    
    # 元数据
    published_at = Column(DateTime, nullable=True, comment="发布时间")
    collected_at = Column(DateTime, server_default=func.now(), comment="收集时间")
    
    # 评分
    score = Column(Float, default=0.0, comment="质量评分")
    
    # 状态
    is_read = Column(Boolean, default=False, comment="是否已读")
    
    # 日期索引（用于按日期查询）
    date_key = Column(String(10), nullable=False, index=True, comment="日期 YYYY-MM-DD")
    
    def __repr__(self):
        return f"<NewsItem {self.id}: {self.title[:50]}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "category": self.category,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "score": self.score,
            "is_read": self.is_read,
            "date_key": self.date_key
        }
