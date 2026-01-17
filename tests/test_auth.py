"""
Tests for authentication endpoints
"""
import time
from fastapi import status


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/users",
        json={"email": "newuser@example.com", "password": "SecurePassword1!"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "username" in data
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/v1/users", json={"email": "test@example.com", "password": "SecurePassword1!"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post("/api/v1/tokens", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post("/api/v1/tokens", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_role(client, test_user):
    """Test adding a role to a user via API"""
    response = client.post(
        f"/api/v1/users/{test_user.id}/roles",
        json={"role": "admin"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["role"] == "admin"
    assert data["user_id"] == test_user.id


def test_add_invalid_role(client, test_user):
    """Test adding an invalid role"""
    response = client.post(
        f"/api/v1/users/{test_user.id}/roles",
        json={"role": "invalid_role"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_role_user_not_found(client):
    """Test adding a role to a non-existent user"""
    response = client.post(
        "/api/v1/users/nonexistent_id/roles",
        json={"role": "user"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_refresh_token(client, test_user):
    """Test refreshing access token"""
    # Login to get initial token
    login_response = client.post("/api/v1/tokens", data={"username": "testuser", "password": "testpassword"})
    initial_token = login_response.json()["access_token"]
    
    # Wait for 1 second to ensure token expiration changes
    time.sleep(1)

    # Refresh token
    response = client.post(
        "/api/v1/token-renewals",
        headers={"Authorization": f"Bearer {initial_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    new_token = data["access_token"]
    assert new_token != initial_token
    
    # Verify new token works
    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {new_token}"}
    )
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["username"] == "testuser"
