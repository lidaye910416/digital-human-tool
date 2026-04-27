from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from src.models.user import User

def create_user(db: Session, username: str, email: str, password: str) -> User:
    password_hash = bcrypt.hash(password)
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        credits=100
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.verify(password, user.password_hash):
        return user
    return None

def deduct_credits(db: Session, user_id: int, amount: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.credits >= amount:
        user.credits -= amount
        db.commit()
        return True
    return False

def add_credits(db: Session, user_id: int, amount: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.credits += amount
        db.commit()
        return True
    return False
