"""
Authentication service
"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.base import SessionLocal
from app.db.models import Role, RoleType, User
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
        """Create a new user and assign default 'user' role"""
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

        # Assign default 'user' role
        default_role = Role(user_id=db_user.id, role=RoleType.user)
        self.db.add(default_role)
        self.db.commit()

        # Convert timestamps to epoch
        created_at_epoch = int(db_user.created_at.timestamp()) if db_user.created_at else 0
        updated_at_epoch = int(db_user.updated_at.timestamp()) if db_user.updated_at else created_at_epoch
        
        return UserResponse(
            id=db_user.id,  # type: ignore[arg-type]
            username=db_user.username,  # type: ignore[arg-type]
            email=db_user.email,  # type: ignore[arg-type]
            is_active=db_user.is_active,  # type: ignore[arg-type]
            created_at=created_at_epoch,
            updated_at=updated_at_epoch,
        )

    async def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user"""
        # Allow login by username or email
        user = self.db.query(User).filter((User.username == username) | (User.email == username)).first()
        if not user:
            return None

        if not verify_password(password, user.hashed_password):  # type: ignore[arg-type]
            return None

        if not user.is_active:
            return None

        # Convert timestamps to epoch
        created_at_epoch = int(user.created_at.timestamp()) if user.created_at else 0
        updated_at_epoch = int(user.updated_at.timestamp()) if user.updated_at else created_at_epoch

        return UserResponse(
            id=user.id,  # type: ignore[arg-type]
            username=user.username,  # type: ignore[arg-type]
            email=user.email,  # type: ignore[arg-type]
            is_active=user.is_active,  # type: ignore[arg-type]
            created_at=created_at_epoch,
            updated_at=updated_at_epoch,
        )

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None

        # Convert timestamps to epoch
        created_at_epoch = int(user.created_at.timestamp()) if user.created_at else 0
        updated_at_epoch = int(user.updated_at.timestamp()) if user.updated_at else created_at_epoch

        return UserResponse(
            id=user.id,  # type: ignore[arg-type]
            username=user.username,  # type: ignore[arg-type]
            email=user.email,  # type: ignore[arg-type]
            is_active=user.is_active,  # type: ignore[arg-type]
            created_at=created_at_epoch,
            updated_at=updated_at_epoch,
        )

    async def add_role_to_user(self, user_id: str, role: RoleType) -> Optional[Role]:
        """Add a role to a user
        user_id can be either the user's UUID (id) or username
        """
        # Try to find user by ID first (UUID format)
        user = self.db.query(User).filter(User.id == user_id).first()
        # If not found, try username
        if not user:
            user = self.db.query(User).filter(User.username == user_id).first()
        if not user:
            return None

        # check if role already exists
        existing_role = self.db.query(Role).filter(Role.user_id == user.id, Role.role == role).first()  # type: ignore[arg-type]
        if existing_role:
            return existing_role

        new_role = Role(user_id=user.id, role=role)
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        return new_role

    async def get_user_roles(self, user_id: str) -> Optional[List[Role]]:
        """Get all roles for a user
        user_id can be either the user's UUID (id) or username
        Also ensures the user has a default 'user' role if no roles exist
        """
        # Try to find user by ID first (UUID format)
        user = self.db.query(User).filter(User.id == user_id).first()
        # If not found, try username
        if not user:
            user = self.db.query(User).filter(User.username == user_id).first()
        if not user:
            return None

        # Get all roles for the user
        roles = self.db.query(Role).filter(Role.user_id == user.id).all()

        # If user has no roles, assign default 'user' role
        if not roles:
            default_role = Role(user_id=user.id, role=RoleType.user)
            self.db.add(default_role)
            self.db.commit()
            self.db.refresh(default_role)
            return [default_role]

        return roles
