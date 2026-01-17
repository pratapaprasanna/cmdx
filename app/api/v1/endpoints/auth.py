"""
Authentication endpoints
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.db.base import get_db
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
async def get_current_user_info(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user information"""
    auth_service = AuthService(db=db)
    user = await auth_service.get_user_by_username(current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/users/{user_id}/roles", response_model=RolesResponse)
async def get_user_roles(user_id: str, db: Session = Depends(get_db)):
    """Get all roles for a user (user_id can be UUID or username)"""
    auth_service = AuthService(db=db)
    roles = await auth_service.get_user_roles(user_id=user_id)
    if roles is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
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
async def add_role(user_id: str, role_data: RoleCreate, db: Session = Depends(get_db)):
    """Add a role to a user"""
    auth_service = AuthService(db=db)
    role = await auth_service.add_role_to_user(user_id=user_id, role=role_data.role)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return role
