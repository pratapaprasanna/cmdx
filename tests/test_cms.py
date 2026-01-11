"""
Tests for CMS endpoints
"""
from fastapi import status


def test_list_plugins(client, auth_headers):
    """Test listing available plugins"""
    response = client.get("/api/v1/cms/plugins", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    plugins = response.json()
    assert isinstance(plugins, list)
    assert "database" in plugins
    assert "filesystem" in plugins


def test_create_content(client, auth_headers):
    """Test creating content"""
    response = client.post(
        "/api/v1/cms/content",
        json={"title": "Test Content", "body": "This is test content", "metadata": {"author": "test"}},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Content"
    assert data["body"] == "This is test content"
    assert "id" in data


def test_get_content(client, auth_headers):
    """Test getting content by ID"""
    # First create content
    create_response = client.post(
        "/api/v1/cms/content", json={"title": "Test Content", "body": "This is test content"}, headers=auth_headers
    )
    content_id = create_response.json()["id"]

    # Then get it
    response = client.get(f"/api/v1/cms/content/{content_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == content_id
    assert data["title"] == "Test Content"


def test_update_content(client, auth_headers):
    """Test updating content"""
    # Create content
    create_response = client.post(
        "/api/v1/cms/content", json={"title": "Original Title", "body": "Original body"}, headers=auth_headers
    )
    content_id = create_response.json()["id"]

    # Update it
    response = client.put(
        f"/api/v1/cms/content/{content_id}",
        json={"title": "Updated Title", "body": "Updated body"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["body"] == "Updated body"


def test_delete_content(client, auth_headers):
    """Test deleting content"""
    # Create content
    create_response = client.post(
        "/api/v1/cms/content", json={"title": "To Delete", "body": "This will be deleted"}, headers=auth_headers
    )
    content_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/cms/content/{content_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(f"/api/v1/cms/content/{content_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_list_content(client, auth_headers):
    """Test listing content"""
    # Create some content
    for i in range(3):
        client.post("/api/v1/cms/content", json={"title": f"Content {i}", "body": f"Body {i}"}, headers=auth_headers)

    # List it
    response = client.get("/api/v1/cms/content", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3


def test_cms_requires_authentication(client):
    """Test that CMS endpoints require authentication"""
    response = client.get("/api/v1/cms/plugins")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
