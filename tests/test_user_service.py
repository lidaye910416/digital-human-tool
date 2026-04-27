import pytest
from src.models.user import User
from src.models.database import SessionLocal, Base, engine
from src.services.user_service import create_user, authenticate_user, deduct_credits

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    user = create_user(db, "testuser", "test@example.com", "password123")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.credits == 100

def test_authenticate_user(db):
    create_user(db, "testuser", "test@example.com", "password123")
    user = authenticate_user(db, "testuser", "password123")
    assert user is not None
    
    result = authenticate_user(db, "testuser", "wrongpassword")
    assert result is None

def test_deduct_credits(db):
    user = create_user(db, "testuser", "test@example.com", "password123")
    assert user.credits == 100
    
    success = deduct_credits(db, user.id, 10)
    assert success is True
    
    db.refresh(user)
    assert user.credits == 90
