"""
CMS endpoints
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.endpoints.auth import require_admin_role
from app.schemas.cms import ContentCreate, ContentCreateResponse, ContentResponse, ContentUpdate
from app.services.cms.cms_service import CMSService

router = APIRouter()


def _convert_to_epoch(iso_datetime_str: str) -> int:
    """Convert ISO datetime string to epoch timestamp"""
    try:
        dt = datetime.fromisoformat(iso_datetime_str.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except (ValueError, AttributeError):
        # Fallback: try parsing as is
        try:
            dt = datetime.fromisoformat(iso_datetime_str)
            return int(dt.timestamp())
        except (ValueError, AttributeError):
            return 0


def _convert_result_timestamps(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert created_at and updated_at from ISO strings to epoch timestamps"""
    converted = result.copy()
    if "created_at" in converted and isinstance(converted["created_at"], str):
        converted["created_at"] = _convert_to_epoch(converted["created_at"])
    if "updated_at" in converted and isinstance(converted["updated_at"], str):
        converted["updated_at"] = _convert_to_epoch(converted["updated_at"])
    return converted


@router.get("/plugins", response_model=List[str])
async def list_plugins(_current_user: str = Depends(require_admin_role)):
    """List available CMS plugins (Admin only)"""
    cms_service = CMSService()
    return cms_service.get_available_plugins()


@router.post("/contents", response_model=ContentCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ContentCreate,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(require_admin_role),
):
    """Create new content"""
    cms_service = CMSService()
    try:
        content_data = content.dict()
        result = await cms_service.create_content(content_data, plugin_name=plugin)
        # Convert timestamps to epoch
        result = _convert_result_timestamps(result)
        
        # Create response without full body to avoid large responses
        body = result.get("body", "")
        body_preview = body[:200] + "..." if len(body) > 200 else body
        return ContentCreateResponse(
            id=result["id"],
            title=result["title"],
            metadata=result.get("metadata", {}),
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            plugin=result.get("plugin"),
            body_preview=body_preview if body_preview else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/contents/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(require_admin_role),
):
    """Get content by ID"""
    cms_service = CMSService()
    try:
        result = await cms_service.get_content(content_id, plugin_name=plugin)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        result = _convert_result_timestamps(result)
        return ContentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/contents/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    content: ContentUpdate,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(require_admin_role),
):
    """Update existing content"""
    cms_service = CMSService()
    try:
        content_data = content.dict(exclude_unset=True)
        result = await cms_service.update_content(content_id, content_data, plugin_name=plugin)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        result = _convert_result_timestamps(result)
        return ContentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/contents/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    _current_user: str = Depends(require_admin_role),
):
    """Delete content"""
    cms_service = CMSService()
    try:
        success = await cms_service.delete_content(content_id, plugin_name=plugin)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/contents", response_model=List[ContentResponse])
async def list_content(
    plugin: Optional[str] = Query(None, description="Plugin name to use"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _current_user: str = Depends(require_admin_role),
):
    """List all content with pagination"""
    cms_service = CMSService()
    try:
        results = await cms_service.list_content(plugin_name=plugin, limit=limit, offset=offset)
        return [ContentResponse(**_convert_result_timestamps(item)) for item in results]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
