"""
CMS schemas
"""
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ContentBase(BaseModel):
    """Base content schema"""

    title: str
    body: str
    metadata: Optional[Dict[str, Any]] = {}


class ContentCreate(BaseModel):
    """Content creation schema"""

    title: str
    body: Optional[str] = None
    file_path: Optional[str] = None  # Path to PDF file (for filesystem plugin)
    metadata: Optional[Dict[str, Any]] = {}
    id: Optional[str] = None


class ContentUpdate(BaseModel):
    """Content update schema"""

    title: Optional[str] = None
    body: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentResponse(ContentBase):
    """Content response schema"""

    id: str
    created_at: int  # Epoch timestamp in seconds
    updated_at: int  # Epoch timestamp in seconds
    plugin: Optional[str] = None

    class Config:
        from_attributes = True


class ContentCreateResponse(BaseModel):
    """Content creation response schema (excludes body to avoid large responses)"""

    id: str
    title: str
    metadata: Optional[Dict[str, Any]] = {}
    created_at: int  # Epoch timestamp in seconds
    updated_at: int  # Epoch timestamp in seconds
    plugin: Optional[str] = None
    body_preview: Optional[str] = None  # First 200 characters of body

    class Config:
        from_attributes = True
