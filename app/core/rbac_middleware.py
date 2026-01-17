"""
Role-Based Access Control Middleware for FastAPI
"""
import re
from typing import Callable

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.security import decode_access_token
from app.db.base import SessionLocal
from app.db.models import Role, RoleType, User


class RBACMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically enforces role-based access control
    based on URL path patterns.
    
    Configuration:
    - CMS paths (/api/v1/plugins, /api/v1/contents) require "admin" role
    - LMS paths (/api/v1/courses, /api/v1/enrollments) require "user" role
    - Course content paths require "user" role
    - Public paths (/api/v1/users, /api/v1/tokens) require no authentication
    - Auth-only paths (/api/v1/users/me, /api/v1/token-renewals) require authentication but no specific role
    """

    # Path patterns to required role mapping
    # Uses regex patterns to match paths
    PATH_ROLE_MAPPING = [
        # CMS endpoints require admin role
        (re.compile(r"^/api/v1/plugins"), RoleType.admin),
        (re.compile(r"^/api/v1/contents"), RoleType.admin),
        # LMS endpoints require user role (GET endpoints require authentication)
        # POST/PUT/DELETE require admin (handled by endpoint dependencies)
        (re.compile(r"^/api/v1/courses"), RoleType.user),
        (re.compile(r"^/api/v1/enrollments"), RoleType.user),
        (re.compile(r"^/api/v1/my-courses"), RoleType.user),
        # Course content management endpoints require admin (handled by endpoint dependencies)
    ]

    # Public paths that don't require authentication
    PUBLIC_PATHS = [
        "/api/v1/users",  # POST - register
        "/api/v1/tokens",  # POST - login
    ]
    
    # Paths that require authentication but not specific role
    # These paths handle their own authorization logic (e.g., admin or self-access)
    AUTH_ONLY_PATHS = [
        "/api/v1/token-renewals",  # POST - renew token
        "/api/v1/users/me",  # GET - current user info
    ]
    
    # Paths that require authentication but have custom authorization logic
    # These are checked in the endpoint itself (e.g., admin or self-access)
    AUTH_WITH_CUSTOM_LOGIC = [
        re.compile(r"^/api/v1/users/[^/]+/roles$"),  # GET/POST /users/{user_id}/roles
    ]

    def __init__(self, app, enabled: bool = True):
        """
        Initialize RBAC middleware
        
        Args:
            app: FastAPI application
            enabled: Whether to enable RBAC checks (default: True)
        """
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and enforce RBAC if needed
        """
        # Skip RBAC if disabled
        if not self.enabled:
            return await call_next(request)  # type: ignore[no-any-return]

        # Skip for public paths (no auth required)
        if request.url.path in self.PUBLIC_PATHS and request.method == "POST":
            return await call_next(request)  # type: ignore[no-any-return]
        
        # Check if path requires auth but has custom authorization logic
        requires_auth_only = False
        for pattern in self.AUTH_WITH_CUSTOM_LOGIC:
            if pattern.match(request.url.path):
                requires_auth_only = True
                break
        
        # Skip RBAC for auth-only paths (just need authentication, no specific role)
        if request.url.path in self.AUTH_ONLY_PATHS or requires_auth_only:
            # Still validate token but don't check roles
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": 401,
                        "developerMessage": "Authentication required",
                        "userMessage": "Please provide a valid authentication token",
                        "errorCode": "AUTHENTICATION_REQUIRED",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            token = auth_header.replace("Bearer ", "")
            payload = decode_access_token(token)
            if payload is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": 401,
                        "developerMessage": "Invalid or expired token",
                        "userMessage": "Authentication failed",
                        "errorCode": "INVALID_TOKEN",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            username = payload.get("sub")
            if username:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.username == username).first()
                    if user:
                        request.state.user = username
                        request.state.user_id = user.id
                        # Also fetch user roles for custom authorization logic in endpoints
                        roles = db.query(Role).filter(Role.user_id == user.id).all()
                        user_roles = [role.role for role in roles] if roles else [RoleType.user]
                        request.state.user_roles = user_roles
                finally:
                    db.close()
            
            return await call_next(request)  # type: ignore[no-any-return]

        # Check if path requires RBAC based on path patterns
        required_role = None
        path = request.url.path
        
        for pattern, role in self.PATH_ROLE_MAPPING:
            if pattern.match(path):
                required_role = role
                break

        # If no role required for this path, proceed
        if required_role is None:
            return await call_next(request)  # type: ignore[no-any-return]

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": 401,
                    "developerMessage": "Authentication required",
                    "userMessage": "Please provide a valid authentication token",
                    "errorCode": "AUTHENTICATION_REQUIRED",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.replace("Bearer ", "")

        # Decode token
        payload = decode_access_token(token)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": 401,
                    "developerMessage": "Invalid or expired token",
                    "userMessage": "Authentication failed",
                    "errorCode": "INVALID_TOKEN",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if not username:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": 401,
                    "developerMessage": "Invalid token payload",
                    "userMessage": "Authentication failed",
                    "errorCode": "INVALID_TOKEN",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user and roles from database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                db.close()
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": 401,
                        "developerMessage": "User not found",
                        "userMessage": "Authentication failed",
                        "errorCode": "USER_NOT_FOUND",
                    },
                )

            # Get user roles
            roles = db.query(Role).filter(Role.user_id == user.id).all()
            user_roles = [role.role for role in roles] if roles else [RoleType.user]

            # Check if user has required role
            # Admin users can access endpoints that require user role
            has_required_role = required_role in user_roles
            is_admin = RoleType.admin in user_roles
            requires_user_role = required_role == RoleType.user
            
            if not has_required_role and not (is_admin and requires_user_role):
                db.close()
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "status": 403,
                        "developerMessage": f"{required_role.value.capitalize()} role required to access this endpoint",
                        "userMessage": "You don't have permission to access this resource",
                        "errorCode": "INSUFFICIENT_PERMISSIONS",
                    },
                )

            # Store user info in request state for use in route handlers
            request.state.user = username
            request.state.user_id = user.id
            request.state.user_roles = user_roles

        finally:
            db.close()

        # Proceed with request
        return await call_next(request)  # type: ignore[no-any-return]
