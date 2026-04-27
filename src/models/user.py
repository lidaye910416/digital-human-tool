from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.models.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    credits = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
