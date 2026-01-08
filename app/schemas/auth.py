"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str

