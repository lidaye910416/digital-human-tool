import pytest
from src.models.database import SessionLocal, Base, engine
from src.models.user import User
from src.services.analytics_service import AnalyticsService

# 导入所有模型以确保表创建
from src.models.avatar import Avatar
from src.models.video_project import VideoProject
from src.models.scene import Scene

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_user_stats(db):
    user = User(username="test", email="test@test.com", password_hash="x", credits=100)
    db.add(user)
    db.commit()
    service = AnalyticsService()
    stats = service.get_user_stats(db, user.id)
    assert stats["total_credits"] == 100
    assert stats["total_projects"] == 0
