"""
LMS endpoints
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List as ListType
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.base import get_db
from app.db.models import User
from app.schemas.lms import CourseCreate, CourseResponse, CourseUpdate, EnrollmentRequest
from app.services.lms.lms_service import LMSService

router = APIRouter()


async def get_current_user_id(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)) -> str:
    """Get current user ID from username"""
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.id  # type: ignore[return-value]


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate, _current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Create a new course"""
    lms_service = LMSService(db=db)
    course_data = course.dict()
    result = await lms_service.create_course(course_data)
    return CourseResponse(**result)


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    resolve_content: bool = Query(False, description="Resolve CMS content in modules"),
    _current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get course by ID with optional content resolution"""
    lms_service = LMSService(db=db)
    result = await lms_service.get_course(course_id, resolve_content=resolve_content)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseResponse(**result)


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str, course: CourseUpdate, _current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Update existing course"""
    lms_service = LMSService(db=db)
    course_data = course.dict(exclude_unset=True)
    result = await lms_service.update_course(course_id, course_data)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseResponse(**result)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: str, _current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete course"""
    lms_service = LMSService(db=db)
    success = await lms_service.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all courses with pagination"""
    lms_service = LMSService(db=db)
    results = await lms_service.list_courses(limit=limit, offset=offset)
    return [CourseResponse(**item) for item in results]


@router.post("/enrollments", status_code=status.HTTP_201_CREATED)
async def enroll_user(
    enrollment: EnrollmentRequest, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Enroll a user in a course"""
    lms_service = LMSService(db=db)
    # Use enrollment.user_id if provided, otherwise use current user
    if enrollment.user_id:
        user_id = enrollment.user_id
    else:
        user_id = await get_current_user_id(current_user, db)
    success = await lms_service.enroll_user(user_id, enrollment.course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found or enrollment failed")
    return {"message": "Enrollment successful"}


@router.delete("/enrollments/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_user(course_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Unenroll a user from a course"""
    lms_service = LMSService(db=db)
    user_id = await get_current_user_id(current_user, db)
    success = await lms_service.unenroll_user(user_id, course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")


@router.get("/my-courses", response_model=List[CourseResponse])
async def get_my_courses(
    resolve_content: bool = Query(False, description="Resolve CMS content in modules"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all courses the current user is enrolled in"""
    lms_service = LMSService(db=db)
    user_id = await get_current_user_id(current_user, db)
    results = await lms_service.get_user_courses(user_id)
    
    if resolve_content:
        from app.services.lms.course_content_resolver import CourseContentResolver
        resolver = CourseContentResolver()
        resolved_results = []
        for course in results:
            resolved_course = await resolver.resolve_course_modules(course, include_content=True)
            resolved_results.append(resolved_course)
        return [CourseResponse(**item) for item in resolved_results]
    
    return [CourseResponse(**item) for item in results]
