"""
Learning Management System service using PostgreSQL
"""
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db.models import Course as CourseModel
from app.db.models import User
from app.services.lms.course_content_resolver import CourseContentResolver


class LMSService:
    """Service for learning management operations"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()

    async def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new course"""
        course_id = course_data.get("id") or f"course_{uuid.uuid4().hex[:8]}"

        db_course = CourseModel(
            id=course_id,
            title=course_data.get("title", ""),
            description=course_data.get("description", ""),
            instructor=course_data.get("instructor", ""),
            modules=course_data.get("modules", []),
        )
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)

        return {
            "id": db_course.id,
            "title": db_course.title,
            "description": db_course.description,
            "instructor": db_course.instructor,
            "modules": db_course.modules or [],
            "created_at": db_course.created_at.isoformat() if db_course.created_at else None,
            "updated_at": db_course.updated_at.isoformat() if db_course.updated_at else None,
        }

    async def get_course(
        self, course_id: str, resolve_content: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get course by ID

        Args:
            course_id: Course ID
            resolve_content: If True, resolve CMS content in modules

        Returns:
            Course data with optionally resolved content
        """
        course = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            return None

        course_data = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor": course.instructor,
            "modules": course.modules or [],
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "updated_at": course.updated_at.isoformat() if course.updated_at else None,
        }

        if resolve_content:
            resolver = CourseContentResolver()
            course_data = await resolver.resolve_course_modules(course_data, include_content=True)

        return course_data

    async def update_course(self, course_id: str, course_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing course"""
        course = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            return None

        if "title" in course_data:
            course.title = course_data["title"]
        if "description" in course_data:
            course.description = course_data["description"]
        if "instructor" in course_data:
            course.instructor = course_data["instructor"]
        if "modules" in course_data:
            course.modules = course_data["modules"]

        self.db.commit()
        self.db.refresh(course)

        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor": course.instructor,
            "modules": course.modules or [],
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "updated_at": course.updated_at.isoformat() if course.updated_at else None,
        }

    async def delete_course(self, course_id: str) -> bool:
        """Delete course"""
        course = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            return False

        self.db.delete(course)
        self.db.commit()
        return True

    async def list_courses(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all courses with pagination"""
        courses = self.db.query(CourseModel).offset(offset).limit(limit).all()

        return [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "instructor": course.instructor,
                "modules": course.modules or [],
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "updated_at": course.updated_at.isoformat() if course.updated_at else None,
            }
            for course in courses
        ]

    async def enroll_user(self, user_id: str, course_id: str) -> bool:
        """Enroll a user in a course"""
        course = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
        user = self.db.query(User).filter(User.id == user_id).first()

        if not course or not user:
            return False

        # Check if already enrolled
        if course in user.enrollments:
            return True

        user.enrollments.append(course)
        self.db.commit()
        return True

    async def unenroll_user(self, user_id: str, course_id: str) -> bool:
        """Unenroll a user from a course"""
        course = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
        user = self.db.query(User).filter(User.id == user_id).first()

        if not course or not user:
            return False

        if course not in user.enrollments:
            return False

        user.enrollments.remove(course)
        self.db.commit()
        return True

    async def get_user_courses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all courses a user is enrolled in"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        return [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "instructor": course.instructor,
                "modules": course.modules or [],
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "updated_at": course.updated_at.isoformat() if course.updated_at else None,
            }
            for course in user.enrollments
        ]
