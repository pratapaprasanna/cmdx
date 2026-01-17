"""
Standardized error handling following White House Web API Standards
"""
from typing import Optional

from fastapi import HTTPException, status


class APIException(HTTPException):
    """Standardized API exception following White House Web API Standards"""

    def __init__(
        self,
        status_code: int,
        developer_message: str,
        user_message: Optional[str] = None,
        error_code: Optional[str] = None,
        more_info: Optional[str] = None,
    ):
        """
        Create a standardized API exception

        Args:
            status_code: HTTP status code
            developer_message: Detailed technical error message for developers
            user_message: User-friendly error message (defaults to developer_message)
            error_code: Machine-readable error code (e.g., "USER_NOT_FOUND")
            more_info: URL to documentation about this error
        """
        detail = {
            "status": status_code,
            "developerMessage": developer_message,
            "userMessage": user_message or developer_message,
        }
        if error_code:
            detail["errorCode"] = error_code
        if more_info:
            detail["moreInfo"] = more_info

        super().__init__(status_code=status_code, detail=detail)


def raise_not_found(resource_type: str, resource_id: str, error_code: Optional[str] = None):
    """Raise a standardized 404 Not Found error"""
    error_code = error_code or f"{resource_type.upper()}_NOT_FOUND"
    raise APIException(
        status_code=status.HTTP_404_NOT_FOUND,
        developer_message=f"{resource_type.capitalize()} with id '{resource_id}' not found",
        user_message=f"{resource_type.capitalize()} not found",
        error_code=error_code,
    )


def raise_bad_request(message: str, error_code: Optional[str] = None):
    """Raise a standardized 400 Bad Request error"""
    raise APIException(
        status_code=status.HTTP_400_BAD_REQUEST,
        developer_message=message,
        user_message="Invalid request",
        error_code=error_code or "BAD_REQUEST",
    )


def raise_unauthorized(message: str = "Invalid authentication credentials"):
    """Raise a standardized 401 Unauthorized error"""
    raise APIException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        developer_message=message,
        user_message="Authentication required",
        error_code="UNAUTHORIZED",
    )


def raise_forbidden(message: str = "Access denied"):
    """Raise a standardized 403 Forbidden error"""
    raise APIException(
        status_code=status.HTTP_403_FORBIDDEN,
        developer_message=message,
        user_message="You don't have permission to access this resource",
        error_code="FORBIDDEN",
    )


def raise_conflict(message: str, error_code: Optional[str] = None):
    """Raise a standardized 409 Conflict error"""
    raise APIException(
        status_code=status.HTTP_409_CONFLICT,
        developer_message=message,
        user_message="Resource conflict",
        error_code=error_code or "CONFLICT",
    )
