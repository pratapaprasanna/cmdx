"""
LMS schemas
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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

    user_id: str
    course_id: str
