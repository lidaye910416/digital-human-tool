"""技术咨询数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from src.models.database import Base
import enum

class ConsultationStatus(str, enum.Enum):
    PENDING = "pending"       # 待处理
    READ = "read"             # 已查看
    REPLIED = "replied"       # 已回复
    ARCHIVED = "archived"      # 已归档

class Consultation(Base):
    """技术咨询表"""
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="咨询标题")
    content = Column(Text, nullable=False, comment="咨询内容")
    contact = Column(String(100), nullable=True, comment="联系方式")
    source = Column(String(50), default="web", comment="来源: web, wechat, miniapp")
    
    # 状态
    status = Column(String(20), default=ConsultationStatus.PENDING.value)
    
    # 日期存储
    consultation_date = Column(String(10), nullable=False, comment="咨询日期 YYYY-MM-DD")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联
    user_id = Column(Integer, default=1)
    avatar_id = Column(Integer, nullable=True, comment="使用的数字人ID")
    voice_id = Column(String(50), nullable=True, comment="使用的声音ID")
    
    def __repr__(self):
        return f"<Consultation {self.id}: {self.title}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "contact": self.contact,
            "source": self.source,
            "status": self.status,
            "consultation_date": self.consultation_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "avatar_id": self.avatar_id,
            "voice_id": self.voice_id
        }
