"""
Tests for LMS endpoints
"""
from fastapi import status


def test_create_course(client, auth_headers):
    """Test creating a course"""
    response = client.post(
        "/api/v1/courses",
        json={
            "title": "Python 101",
            "description": "Introduction to Python",
            "instructor": "John Doe",
            "modules": [{"name": "Basics", "lessons": []}],
        },
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Python 101"
    assert data["description"] == "Introduction to Python"
    assert "id" in data


def test_get_course(client, auth_headers):
    """Test getting a course by ID"""
    # Create course
    create_response = client.post(
        "/api/v1/courses",
        json={"title": "Test Course", "description": "Test Description", "instructor": "Test Instructor"},
        headers=auth_headers,
    )
    course_id = create_response.json()["id"]

    # Get it
    response = client.get(f"/api/v1/courses/{course_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == course_id
    assert data["title"] == "Test Course"


def test_update_course(client, auth_headers):
    """Test updating a course"""
    # Create course
    create_response = client.post(
        "/api/v1/courses",
        json={"title": "Original Title", "description": "Original Description", "instructor": "Original Instructor"},
        headers=auth_headers,
    )
    course_id = create_response.json()["id"]

    # Update it
    response = client.put(
        f"/api/v1/courses/{course_id}",
        json={"title": "Updated Title", "description": "Updated Description"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"


def test_delete_course(client, auth_headers):
    """Test deleting a course"""
    # Create course
    create_response = client.post(
        "/api/v1/courses",
        json={"title": "To Delete", "description": "Will be deleted", "instructor": "Instructor"},
        headers=auth_headers,
    )
    course_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/courses/{course_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(f"/api/v1/courses/{course_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_list_courses(client, auth_headers):
    """Test listing courses"""
    # Create some courses
    for i in range(3):
        client.post(
            "/api/v1/courses",
            json={"title": f"Course {i}", "description": f"Description {i}", "instructor": f"Instructor {i}"},
            headers=auth_headers,
        )

    # List them
    response = client.get("/api/v1/courses", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3


def test_enroll_user(client, auth_headers, test_user):
    """Test enrolling a user in a course"""
    # Create course
    create_response = client.post(
        "/api/v1/courses",
        json={"title": "Enrollment Test", "description": "Test Description", "instructor": "Instructor"},
        headers=auth_headers,
    )
    course_id = create_response.json()["id"]

    # Enroll user
    response = client.post(
        "/api/v1/enrollments", json={"user_id": str(test_user.id), "course_id": course_id}, headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_get_my_courses(client, auth_headers, test_user):
    """Test getting user's enrolled courses"""
    # Create and enroll in a course
    create_response = client.post(
        "/api/v1/courses",
        json={"title": "My Course", "description": "My Description", "instructor": "Instructor"},
        headers=auth_headers,
    )
    course_id = create_response.json()["id"]

    # Enroll
    client.post(
        "/api/v1/enrollments", json={"user_id": str(test_user.id), "course_id": course_id}, headers=auth_headers
    )

    # Get my courses
    response = client.get("/api/v1/my-courses", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(course["id"] == course_id for course in data)


def test_lms_requires_authentication(client):
    """Test that LMS endpoints require authentication"""
    response = client.get("/api/v1/courses")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
