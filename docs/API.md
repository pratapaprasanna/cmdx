# API Documentation

## Authentication

All endpoints except `/api/v1/auth/register` and `/api/v1/auth/login` require authentication via Bearer token.

### Register User

**POST** `/api/v1/auth/register`

Request body:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

Response: `201 Created`
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### Login

**POST** `/api/v1/auth/login`

Form data:
- `username`: string
- `password`: string

Response: `200 OK`
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Get Current User

**GET** `/api/v1/auth/me`

Headers: `Authorization: Bearer <token>`

Response: `200 OK`
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

## CMS Endpoints

### List Plugins

**GET** `/api/v1/cms/plugins`

Response: `200 OK`
```json
["database", "filesystem"]
```

### Create Content

**POST** `/api/v1/cms/content?plugin=database`

Query parameters:
- `plugin` (optional): "database" or "filesystem" (default: "database")

Request body:
```json
{
  "title": "string",
  "body": "string",
  "metadata": {},
  "id": "string (optional)"
}
```

Response: `201 Created`
```json
{
  "id": "string",
  "title": "string",
  "body": "string",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "plugin": "database"
}
```

### Get Content

**GET** `/api/v1/cms/content/{content_id}?plugin=database`

Response: `200 OK`
```json
{
  "id": "string",
  "title": "string",
  "body": "string",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "plugin": "database"
}
```

### Update Content

**PUT** `/api/v1/cms/content/{content_id}?plugin=database`

Request body:
```json
{
  "title": "string (optional)",
  "body": "string (optional)",
  "metadata": {} (optional)
}
```

Response: `200 OK`
```json
{
  "id": "string",
  "title": "string",
  "body": "string",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "plugin": "database"
}
```

### Delete Content

**DELETE** `/api/v1/cms/content/{content_id}?plugin=database`

Response: `204 No Content`

### List Content

**GET** `/api/v1/cms/content?plugin=database&limit=100&offset=0`

Query parameters:
- `plugin` (optional): "database" or "filesystem"
- `limit` (optional): Number of items to return (default: 100, max: 1000)
- `offset` (optional): Number of items to skip (default: 0)

Response: `200 OK`
```json
[
  {
    "id": "string",
    "title": "string",
    "body": "string",
    "metadata": {},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "plugin": "database"
  }
]
```

## LMS Endpoints

### Create Course

**POST** `/api/v1/lms/courses`

Request body:
```json
{
  "title": "string",
  "description": "string",
  "instructor": "string",
  "modules": [],
  "id": "string (optional)"
}
```

Response: `201 Created`
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "instructor": "string",
  "modules": [],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Get Course

**GET** `/api/v1/lms/courses/{course_id}`

Response: `200 OK`
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "instructor": "string",
  "modules": [],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Update Course

**PUT** `/api/v1/lms/courses/{course_id}`

Request body:
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "instructor": "string (optional)",
  "modules": [] (optional)
}
```

Response: `200 OK`
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "instructor": "string",
  "modules": [],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Delete Course

**DELETE** `/api/v1/lms/courses/{course_id}`

Response: `204 No Content`

### List Courses

**GET** `/api/v1/lms/courses?limit=100&offset=0`

Query parameters:
- `limit` (optional): Number of items to return (default: 100, max: 1000)
- `offset` (optional): Number of items to skip (default: 0)

Response: `200 OK`
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "instructor": "string",
    "modules": [],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### Enroll User

**POST** `/api/v1/lms/enrollments`

Request body:
```json
{
  "user_id": "string",
  "course_id": "string"
}
```

Response: `201 Created`
```json
{
  "message": "Enrollment successful"
}
```

### Unenroll User

**DELETE** `/api/v1/lms/enrollments/{course_id}`

Response: `204 No Content`

### Get My Courses

**GET** `/api/v1/lms/my-courses`

Response: `200 OK`
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "instructor": "string",
    "modules": [],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

## Error Responses

All endpoints follow the **White House Web API Standards** for error handling.

### HTTP Status Codes

- `200 OK`: Successful GET, PUT requests
- `201 Created`: Successful POST that creates a resource
- `204 No Content`: Successful DELETE or PUT that returns no body
- `400 Bad Request`: Invalid request data, validation errors
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate email)
- `422 Unprocessable Entity`: Validation errors (Pydantic)
- `500 Internal Server Error`: Unexpected server errors

### Error Response Format

Following White House Web API Standards, error responses use a standardized format:

```json
{
  "detail": {
    "status": 404,
    "developerMessage": "User with id 'abc123' not found",
    "userMessage": "User not found",
    "errorCode": "USER_NOT_FOUND",
    "moreInfo": "https://api.example.com/docs/errors#USER_NOT_FOUND"
  }
}
```

**Fields:**
- `status`: HTTP status code (integer)
- `developerMessage`: Detailed technical error message for developers
- `userMessage`: User-friendly error message
- `errorCode`: Machine-readable error code (optional)
- `moreInfo`: URL to documentation about this error (optional)

**Note:** Some endpoints may still return simple string error messages in the `detail` field for backward compatibility, but new endpoints should use the standardized format.
