"""
Authentication service
"""
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.base import SessionLocal
from app.db.models import User
from app.schemas.auth import UserResponse


class AuthService:
    """Service for authentication operations"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()

    async def create_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Create a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == email).first()

        if existing_user:
            return None

        # Create new user
        hashed_password = get_password_hash(password)
        username = uuid.uuid4().hex
        db_user = User(username=username, email=email, hashed_password=hashed_password, is_active=True)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
        )

    async def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user"""
        # Allow login by username or email
        user = self.db.query(User).filter((User.username == username) | (User.email == username)).first()
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return UserResponse(
            id=user.id, username=user.username, email=user.email, is_active=user.is_active, created_at=user.created_at
        )

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None

        return UserResponse(
            id=user.id, username=user.username, email=user.email, is_active=user.is_active, created_at=user.created_at
        )
