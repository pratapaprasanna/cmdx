"""
Helper functions for RBAC that work with middleware
"""
from typing import List

from fastapi import HTTPException, Request, status

from app.db.models import RoleType


def get_user_from_request(request: Request) -> str:
    """
    Get username from request state (set by RBAC middleware)
    
    Raises 401 if user not authenticated
    """
    username = getattr(request.state, "user", None)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": 401,
                "developerMessage": "User not authenticated",
                "userMessage": "Authentication required",
                "errorCode": "AUTHENTICATION_REQUIRED",
            },
        )
    return username  # type: ignore[no-any-return]


def get_user_id_from_request(request: Request) -> str:
    """
    Get user ID from request state (set by RBAC middleware)
    
    Raises 401 if user not authenticated
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": 401,
                "developerMessage": "User not authenticated",
                "userMessage": "Authentication required",
                "errorCode": "AUTHENTICATION_REQUIRED",
            },
        )
    return user_id  # type: ignore[no-any-return]


def get_user_roles_from_request(request: Request) -> List[RoleType]:
    """
    Get user roles from request state (set by RBAC middleware)
    
    Returns empty list if no roles found
    """
    return getattr(request.state, "user_roles", [])


def has_role(request: Request, role: RoleType) -> bool:
    """
    Check if user has a specific role
    
    Args:
        request: FastAPI request object
        role: Role to check for
        
    Returns:
        True if user has the role, False otherwise
    """
    user_roles = get_user_roles_from_request(request)
    return role in user_roles


def require_role(request: Request, role: RoleType) -> None:
    """
    Require a specific role, raise 403 if user doesn't have it
    
    Args:
        request: FastAPI request object
        role: Required role
        
    Raises:
        HTTPException(403) if user doesn't have the role
    """
    if not has_role(request, role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": 403,
                "developerMessage": f"{role.value.capitalize()} role required",
                "userMessage": "You don't have permission to access this resource",
                "errorCode": "INSUFFICIENT_PERMISSIONS",
            },
        )
