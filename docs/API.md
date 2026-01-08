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

All endpoints may return the following error responses:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message"
}
```

