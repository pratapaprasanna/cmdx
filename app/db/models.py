"""
Database models
"""
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

# Association table for user-course enrollments
user_course_enrollment = Table(
    "user_course_enrollment",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("course_id", String, ForeignKey("courses.id"), primary_key=True),
)


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrollments = relationship("Course", secondary=user_course_enrollment, back_populates="enrolled_users")


class Content(Base):
    """Content model for CMS"""

    __tablename__ = "content"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    meta_data = Column("meta_data", JSON, default={})
    plugin = Column(String, default="database")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Course(Base):
    """Course model for LMS"""

    __tablename__ = "courses"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    instructor = Column(String, nullable=False)
    modules = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrolled_users = relationship("User", secondary=user_course_enrollment, back_populates="enrollments")
