from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from datetime import datetime
from src.models.database import Base

class VideoProject(Base):
    __tablename__ = "video_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    script_text = Column(Text, nullable=False)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    scene_id = Column(String)
    voice_config = Column(JSON)
    status = Column(String, default="pending")
    output_url = Column(String)
    credits_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
