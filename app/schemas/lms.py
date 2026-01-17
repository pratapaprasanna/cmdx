"""
LMS schemas
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    """Base course schema"""

    title: str
    description: str
    instructor: str
    modules: List[Dict[str, Any]] = []


class CourseCreate(CourseBase):
    """Course creation schema"""

    id: Optional[str] = None


class CourseUpdate(BaseModel):
    """Course update schema"""

    title: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    modules: Optional[List[Dict[str, Any]]] = None


class CourseResponse(CourseBase):
    """Course response schema"""

    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class EnrollmentRequest(BaseModel):
    """Enrollment request schema"""

    user_id: Optional[str] = None
    course_id: str


class ModuleContentItem(BaseModel):
    """Content item within a module"""

    content_id: str = Field(..., description="CMS content ID")
    plugin: str = Field(..., description="Plugin name (e.g., 'database', 'filesystem')")
    type: Optional[str] = Field(None, description="Content type (e.g., 'lesson', 'video', 'quiz')")
    order: int = Field(0, description="Display order within module")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CourseModule(BaseModel):
    """Course module schema"""

    id: str = Field(..., description="Module ID")
    title: str = Field(..., description="Module title")
    description: Optional[str] = Field(None, description="Module description")
    order: int = Field(0, description="Module order in course")
    content_items: List[ModuleContentItem] = Field(default_factory=list, description="Content items in module")


class CourseWithContentResponse(CourseResponse):
    """Course response with resolved CMS content"""

    modules: List[Dict[str, Any]] = Field(..., description="Modules with resolved content")
