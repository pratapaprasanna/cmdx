"""
Course content management endpoints
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.base import get_db
from app.db.models import Course as CourseModel
from app.db.models import User
from app.schemas.lms import CourseModule, ModuleContentItem
from app.services.cms.cms_service import CMSService
from app.services.lms.course_content_resolver import CourseContentResolver

router = APIRouter()


async def get_current_user_id(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)) -> str:
    """Get current user ID from username"""
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.id  # type: ignore[return-value]


@router.post("/courses/{course_id}/modules/{module_id}/content", status_code=status.HTTP_201_CREATED)
async def add_content_to_module(
    course_id: str,
    module_id: str,
    content_item: ModuleContentItem,
    _current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add CMS content to a course module"""
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Validate content exists
    cms_service = CMSService()
    try:
        content = await cms_service.get_content(content_item.content_id, plugin_name=content_item.plugin)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content '{content_item.content_id}' not found in plugin '{content_item.plugin}'",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    # Find or create module
    modules = course.modules or []
    module = None
    for m in modules:
        if isinstance(m, dict) and m.get("id") == module_id:
            module = m
            break

    if not module:
        # Create new module
        module = {
            "id": module_id,
            "title": f"Module {module_id}",
            "order": len(modules),
            "content_items": [],
        }
        modules.append(module)

    # Add content item
    if "content_items" not in module:
        module["content_items"] = []

    # Check if content already exists
    for item in module["content_items"]:
        if (
            item.get("content_id") == content_item.content_id
            and item.get("plugin") == content_item.plugin
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Content already exists in module",
            )

    content_item_dict = content_item.dict()
    module["content_items"].append(content_item_dict)

    # Update course
    course.modules = modules
    db.commit()
    db.refresh(course)

    return {"message": "Content added to module", "content_item": content_item_dict}


@router.delete("/courses/{course_id}/modules/{module_id}/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_content_from_module(
    course_id: str,
    module_id: str,
    content_id: str,
    plugin: str = Query(..., description="Plugin name"),
    _current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove CMS content from a course module"""
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    modules = course.modules or []
    for module in modules:
        if isinstance(module, dict) and module.get("id") == module_id:
            content_items = module.get("content_items", [])
            original_count = len(content_items)

            module["content_items"] = [
                item
                for item in content_items
                if not (
                    item.get("content_id") == content_id and item.get("plugin") == plugin
                )
            ]

            if len(module["content_items"]) == original_count:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found in module",
                )

            course.modules = modules
            db.commit()
            return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")


@router.get("/courses/{course_id}/modules/{module_id}/content/validate")
async def validate_module_content(
    course_id: str,
    module_id: str,
    _current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate that all content references in a module exist"""
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    modules = course.modules or []
    for module in modules:
        if isinstance(module, dict) and module.get("id") == module_id:
            resolver = CourseContentResolver()
            validation = await resolver.validate_content_references([module])
            return validation

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
