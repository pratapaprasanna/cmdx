"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, cms, course_content, lms

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(cms.router, tags=["cms"])
api_router.include_router(lms.router, tags=["lms"])
api_router.include_router(course_content.router, tags=["course-content"])