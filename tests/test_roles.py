"""
Tests for role management and database relationships
"""
import uuid

import pytest
from fastapi import status

from app.core.security import get_password_hash
from app.db.models import Role, RoleType


def test_role_database_relationship(db_session):
    """Test that roles can be assigned to users and retrieved via relationship"""
    from app.db.models import User

    # Create a user
    username = f"role_test_user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"

    user = User(username=username, email=email, hashed_password=get_password_hash("testpassword"), is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Add multiple roles
    admin_role = Role(user_id=user.id, role=RoleType.admin)
    dev_role = Role(user_id=user.id, role=RoleType.developer)
    user_role = Role(user_id=user.id, role=RoleType.user)

    db_session.add_all([admin_role, dev_role, user_role])
    db_session.commit()

    # Verify roles via relationship
    db_session.refresh(user)
    assert len(user.roles) == 3

    roles_set = {r.role for r in user.roles}
    expected_roles = {RoleType.admin, RoleType.developer, RoleType.user}
    assert roles_set == expected_roles


def test_get_user_roles_endpoint(client, test_user):
    """Test getting roles for a user via API"""
    # First add some roles
    admin_response = client.post(
        f"/api/v1/users/{test_user.id}/roles",
        json={"role": "admin"},
    )
    assert admin_response.status_code == status.HTTP_201_CREATED

    dev_response = client.post(
        f"/api/v1/users/{test_user.id}/roles",
        json={"role": "developer"},
    )
    assert dev_response.status_code == status.HTTP_201_CREATED

    # Get roles via API
    response = client.get(f"/api/v1/users/{test_user.id}/roles")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user_id" in data
    assert "roles" in data
    assert data["user_id"] == test_user.id
    assert len(data["roles"]) >= 2  # At least admin and developer

    # Verify role types
    role_types = {role["role"] for role in data["roles"]}
    assert "admin" in role_types
    assert "developer" in role_types
    # Note: "user" role is only auto-assigned if user has NO roles
    # Since we added admin and developer, user role won't be auto-added


def test_get_user_roles_by_username(client, test_user):
    """Test getting roles using username instead of UUID"""
    # Add a role first
    admin_response = client.post(
        f"/api/v1/users/{test_user.id}/roles",
        json={"role": "admin"},
    )
    assert admin_response.status_code == status.HTTP_201_CREATED

    # Get roles using username
    response = client.get(f"/api/v1/users/{test_user.username}/roles")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == test_user.id
    assert len(data["roles"]) >= 1  # At least the admin role we added
    role_types = {role["role"] for role in data["roles"]}
    assert "admin" in role_types


def test_get_user_roles_not_found(client):
    """Test getting roles for non-existent user"""
    response = client.get("/api/v1/users/nonexistent_user/roles")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_default_user_role_assigned_on_creation(db_session):
    """Test that new users automatically get the 'user' role"""
    from app.services.auth.auth_service import AuthService

    auth_service = AuthService(db=db_session)

    # Create user via service (which should assign default role)
    user_response = await auth_service.create_user(email="newuser@test.com", password="SecurePassword1!")

    assert user_response is not None

    # Check that user has the default 'user' role
    roles = db_session.query(Role).filter(Role.user_id == user_response.id).all()
    assert len(roles) == 1
    assert roles[0].role == RoleType.user


@pytest.mark.asyncio
async def test_default_user_role_assigned_when_no_roles_exist(db_session):
    """Test that get_user_roles assigns default 'user' role if user has no roles"""
    from app.db.models import User
    from app.services.auth.auth_service import AuthService

    # Create user without roles
    user = User(
        username="noroles_user", email="noroles@test.com", hashed_password=get_password_hash("password"), is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Get roles (should auto-assign default 'user' role)
    auth_service = AuthService(db=db_session)
    roles = await auth_service.get_user_roles(user.id)

    assert roles is not None
    assert len(roles) == 1
    assert roles[0].role == RoleType.user
    assert roles[0].user_id == user.id
