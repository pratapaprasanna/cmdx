"""
CMS endpoints
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.endpoints.auth import get_current_user
from app.schemas.cms import ContentCreate, ContentResponse, ContentUpdate
from app.services.cms.cms_service import CMSService

router = APIRouter()


@router.get("/plugins", response_model=List[str])
async def list_plugins(_current_user: str = Depends(get_current_user)):
    """List available CMS plugins"""
    cms_service = CMSService()
    return cms_service.get_available_plugins()


@router.post("/content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ContentCreate,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(get_current_user),
):
    """Create new content"""
    cms_service = CMSService()
    try:
        content_data = content.dict()
        result = await cms_service.create_content(content_data, plugin_name=plugin)
        return ContentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(get_current_user),
):
    """Get content by ID"""
    cms_service = CMSService()
    try:
        result = await cms_service.get_content(content_id, plugin_name=plugin)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        return ContentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/content/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    content: ContentUpdate,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(get_current_user),
):
    """Update existing content"""
    cms_service = CMSService()
    try:
        content_data = content.dict(exclude_unset=True)
        result = await cms_service.update_content(content_id, content_data, plugin_name=plugin)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        return ContentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(get_current_user),
):
    """Delete content"""
    cms_service = CMSService()
    try:
        success = await cms_service.delete_content(content_id, plugin_name=plugin)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/content", response_model=List[ContentResponse])
async def list_content(
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _current_user: str = Depends(get_current_user),
):
    """List all content with pagination"""
    cms_service = CMSService()
    try:
        results = await cms_service.list_content(plugin_name=plugin, limit=limit, offset=offset)
        return [ContentResponse(**item) for item in results]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
