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


class ContentCreate(ContentBase):
    """Content creation schema"""

    id: Optional[str] = None


class ContentUpdate(BaseModel):
    """Content update schema"""

    title: Optional[str] = None
    body: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentResponse(ContentBase):
    """Content response schema"""

    id: str
    created_at: str
    updated_at: str
    plugin: Optional[str] = None

    class Config:
        from_attributes = True
