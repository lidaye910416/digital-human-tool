import pytest
from src.models.database import SessionLocal, Base, engine
from src.services.scene_service import SceneService

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_get_scenes(db):
    service = SceneService()
    scenes = service.get_all_scenes(db)
    assert isinstance(scenes, list)
