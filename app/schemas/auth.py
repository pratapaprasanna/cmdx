"""
Authentication schemas
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.core.validators import validate_password_strength


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr


class UserCreate(UserBase):
    """User creation schema"""

    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)


class UserLogin(BaseModel):
    """User login schema"""

    username: str
    password: str


class UserResponse(UserBase):
    """User response schema"""

    id: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""

    access_token: str
    token_type: str
