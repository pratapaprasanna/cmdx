"""
Authentication endpoints
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rbac_helpers import get_user_from_request, get_user_id_from_request, get_user_roles_from_request
from app.core.security import create_access_token, decode_access_token
from app.db.base import get_db
from app.db.models import Role, RoleType, User
from app.schemas.auth import RoleCreate, RoleResponse, RolesResponse, Token, UserCreate, UserResponse
from app.services.auth.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/tokens")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from token"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")  # type: ignore[assignment]
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


async def get_current_user_with_roles(
    current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
) -> tuple[str, list[RoleType]]:
    """
    Get current user and their roles
    
    Returns:
        Tuple of (username, list of roles)
    """
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get user roles
    roles = db.query(Role).filter(Role.user_id == user.id).all()  # type: ignore[assignment]
    role_types = [role.role for role in roles] if roles else [RoleType.user]  # Default to user role

    return current_user, role_types


async def require_admin_role(
    current_user_data: tuple[str, list[RoleType]] = Depends(get_current_user_with_roles),
) -> str:
    """
    Dependency that requires admin role
    
    Raises 403 Forbidden if user doesn't have admin role
    """
    username, roles = current_user_data
    if RoleType.admin not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": 403,
                "developerMessage": "Admin role required to access this endpoint",
                "userMessage": "You don't have permission to access this resource",
                "errorCode": "INSUFFICIENT_PERMISSIONS",
            },
        )
    return username


async def require_user_role(
    current_user_data: tuple[str, list[RoleType]] = Depends(get_current_user_with_roles),
) -> str:
    """
    Dependency that requires user role (or any authenticated user)
    
    Since all authenticated users have at least the 'user' role by default,
    this effectively just ensures the user is authenticated.
    """
    username, roles = current_user_data
    # All authenticated users should have at least 'user' role
    # This is mainly for consistency and future extensibility
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": 403,
                "developerMessage": "User role required",
                "userMessage": "You don't have permission to access this resource",
                "errorCode": "INSUFFICIENT_PERMISSIONS",
            },
        )
    return username


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    auth_service = AuthService(db=db)
    user = await auth_service.create_user(email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    return user


@router.post("/tokens", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    auth_service = AuthService(db=db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token-renewals", response_model=Token)
async def renew_token(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Renew access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Re-issue token for the current user (using their username from the decoded token)
    access_token = create_access_token(data={"sub": current_user}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """Get current user information"""
    # Get username from request state (set by RBAC middleware)
    username = get_user_from_request(request)
    # Query database directly to get datetime objects for timestamp conversion
    from datetime import datetime

    from app.db.models import User as UserModel
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Convert timestamps to epoch
    created_at_epoch = int(db_user.created_at.timestamp()) if db_user.created_at and isinstance(db_user.created_at, datetime) else 0
    updated_at_epoch = int(db_user.updated_at.timestamp()) if db_user.updated_at and isinstance(db_user.updated_at, datetime) else created_at_epoch
    
    return UserResponse(
        id=db_user.id,  # type: ignore[arg-type]
        email=db_user.email,  # type: ignore[arg-type]
        username=db_user.username,  # type: ignore[arg-type]
        is_active=db_user.is_active,  # type: ignore[arg-type]
        created_at=created_at_epoch,
        updated_at=updated_at_epoch,
    )


@router.get("/users/{user_id}/roles", response_model=RolesResponse)
async def get_user_roles(user_id: str, request: Request, db: Session = Depends(get_db)):
    """Get all roles for a user (user_id can be UUID or username)
    
    Access control:
    - Admin users can view any user's roles
    - Regular users can only view their own roles
    """
    # Get current user info from request state (set by middleware)
    current_user_id = get_user_id_from_request(request)
    current_username = get_user_from_request(request)
    current_user_roles = get_user_roles_from_request(request)
    
    auth_service = AuthService(db=db)
    roles = await auth_service.get_user_roles(user_id=user_id)
    if roles is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check authorization: admin can access any user's roles, others can only access their own
    target_user_id = str(roles[0].user_id)  # type: ignore[arg-type]
    is_admin = RoleType.admin in current_user_roles
    # Check if accessing own profile: by UUID, by username, or by matching user_id parameter
    is_own_profile = (
        str(current_user_id) == target_user_id or 
        user_id == str(current_user_id) or 
        user_id == current_username
    )
    
    if not is_admin and not is_own_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": 403,
                "developerMessage": "You can only view your own roles unless you are an admin",
                "userMessage": "You don't have permission to access this resource",
                "errorCode": "INSUFFICIENT_PERMISSIONS",
            },
        )
    
    # All roles belong to the same user, so we can use the first role's user_id
    return RolesResponse(
        user_id=roles[0].user_id,  # type: ignore[arg-type]
        roles=[
            RoleResponse(
                id=role.id,  # type: ignore[arg-type]
                user_id=role.user_id,  # type: ignore[arg-type]
                role=role.role,  # type: ignore[arg-type]
            )
            for role in roles
        ],
    )


@router.post("/users/{user_id}/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def add_role(
    user_id: str, 
    role_data: RoleCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Add a role to a user
    
    Access control:
    - Admin users can add roles to any user
    - Regular users cannot add roles (admin only)
    """
    # Get current user info from request state (set by middleware)
    current_user_roles = get_user_roles_from_request(request)
    
    # Only admins can add roles
    if RoleType.admin not in current_user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": 403,
                "developerMessage": "Admin role required to add roles to users",
                "userMessage": "You don't have permission to perform this action",
                "errorCode": "INSUFFICIENT_PERMISSIONS",
            },
        )
    
    auth_service = AuthService(db=db)
    role = await auth_service.add_role_to_user(user_id=user_id, role=role_data.role)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return role
