# API Documentation

## Authentication

All endpoints except `/api/v1/users` (register) and `/api/v1/tokens` (login) require authentication via Bearer token.

### Register User

**POST** `/api/v1/users`

Request body:
```json
{
  "email": "string",
  "password": "string"
}
```

Response: `201 Created`
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Note:** New users are automatically assigned the default "user" role.

### Login

**POST** `/api/v1/tokens`

Form data:
- `username`: string (can be username or email)
- `password`: string

Response: `200 OK`
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Renew Token

**POST** `/api/v1/token-renewals`

Headers: `Authorization: Bearer <token>`

Response: `200 OK`
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Get Current User

**GET** `/api/v1/users/me`

Headers: `Authorization: Bearer <token>`

Response: `200 OK`
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get User Roles

**GET** `/api/v1/users/{user_id}/roles`

Parameters:
- `user_id`: string (can be UUID or username)

Response: `200 OK`
```json
{
  "user_id": "string",
  "roles": [
    {
      "id": "string",
      "user_id": "string",
      "role": "user"
    }
  ]
}
```

**Note:** If a user has no roles, the default "user" role is automatically assigned when querying.

### Add Role to User

**POST** `/api/v1/users/{user_id}/roles`

Parameters:
- `user_id`: string (can be UUID or username)

Request body:
```json
{
  "role": "admin"
}
```

Valid role values: `"admin"`, `"developer"`, `"user"`

Response: `201 Created`
```json
{
  "id": "string",
  "user_id": "string",
  "role": "admin"
}
```

## CMS Endpoints

**⚠️ All CMS endpoints require `admin` role.**

All CMS endpoints require authentication with admin role. Regular users will receive 403 Forbidden.

### List Plugins

**GET** `/api/v1/plugins`

Response: `200 OK`
```json
["database", "filesystem"]
```

### Create Content

**POST** `/api/v1/contents?plugin=database`

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
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "plugin": "database"
}
```

### Get Content

**GET** `/api/v1/contents/{content_id}?plugin=database`

Response: `200 OK`
```json
{
  "id": "string",
  "title": "string",
  "body": "string",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "plugin": "database"
}
```

### Update Content

**PUT** `/api/v1/contents/{content_id}?plugin=database`

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
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "plugin": "database"
}
```

### Delete Content

**DELETE** `/api/v1/contents/{content_id}?plugin=database`

Response: `204 No Content`

### List Content

**GET** `/api/v1/contents?plugin=database&limit=100&offset=0`

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
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "plugin": "database"
  }
]
```

## LMS Endpoints

**✅ All LMS endpoints require `user` role (any authenticated user).**

All LMS endpoints require authentication. Since all users get the `user` role by default, any authenticated user can access LMS endpoints.

### Create Course

**POST** `/api/v1/courses`

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
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Course

**GET** `/api/v1/courses/{course_id}`

Response: `200 OK`
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "instructor": "string",
  "modules": [],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Course

**PUT** `/api/v1/courses/{course_id}`

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
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Delete Course

**DELETE** `/api/v1/courses/{course_id}`

Response: `204 No Content`

### List Courses

**GET** `/api/v1/courses?limit=100&offset=0`

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
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Enroll User

**POST** `/api/v1/enrollments`

Request body:
```json
{
  "user_id": "string (optional)",
  "course_id": "string"
}
```

**Note:** If `user_id` is not provided, the current authenticated user will be enrolled.

Response: `201 Created`
```json
{
  "message": "Enrollment successful"
}
```

### Unenroll User

**DELETE** `/api/v1/enrollments/{course_id}`

**Note:** Unenrolls the current authenticated user from the specified course.

Response: `204 No Content`

### Get My Courses

**GET** `/api/v1/my-courses`

**Note:** Returns all courses the current authenticated user is enrolled in.

Response: `200 OK`
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "instructor": "string",
    "modules": [],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
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

**Note:** Some endpoints may still return simple string error messages in the `detail` field for backward compatibility, but new endpoints should use the standardized format defined in `app/core/exceptions.py`.
