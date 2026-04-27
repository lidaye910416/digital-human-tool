from sqlalchemy import Column, Integer, String, Boolean
from src.models.database import Base

class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    thumbnail_url = Column(String)
    scene_url = Column(String)
    is_active = Column(Boolean, default=True)
