"""
API v1 router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, cms, lms

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cms.router, prefix="/cms", tags=["cms"])
api_router.include_router(lms.router, prefix="/lms", tags=["lms"])

