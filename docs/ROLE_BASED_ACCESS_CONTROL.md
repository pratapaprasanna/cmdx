# Role-Based Access Control (RBAC)

## Overview

The API implements role-based access control where different endpoints require different user roles:

- **CMS Endpoints**: Require `admin` role
- **LMS Endpoints**: Require `user` role (or any authenticated user)
- **Auth Endpoints**: Public (register, login) or authenticated (user info, roles)

## Role Dependencies

### `require_admin_role`
**Location**: `app/api/v1/endpoints/auth.py`

**Purpose**: Ensures the authenticated user has the `admin` role

**Used by**: All CMS endpoints

**Behavior**:
- Checks if user has `admin` role
- Returns 403 Forbidden if user doesn't have admin role
- Returns username if user has admin role

**Example**:
```python
@router.post("/contents")
async def create_content(
    _current_user: str = Depends(require_admin_role),
    ...
):
    # Only admins can access this
```

### `require_user_role`
**Location**: `app/api/v1/endpoints/auth.py`

**Purpose**: Ensures the authenticated user has at least the `user` role

**Used by**: All LMS endpoints

**Behavior**:
- Checks if user has any role (all authenticated users have at least `user` role)
- Returns 403 Forbidden if user has no roles
- Returns username if user is authenticated

**Example**:
```python
@router.get("/courses")
async def list_courses(
    _current_user: str = Depends(require_user_role),
    ...
):
    # Any authenticated user can access this
```

## Endpoint Access Matrix

| Endpoint Category | Required Role | Dependency |
|------------------|---------------|------------|
| `POST /users` | None (Public) | None |
| `POST /tokens` | None (Public) | None |
| `GET /users/me` | Authenticated | `get_current_user` |
| `GET /users/{id}/roles` | Authenticated | `get_current_user` |
| `POST /users/{id}/roles` | Authenticated | `get_current_user` |
| **All CMS endpoints** | **Admin** | `require_admin_role` |
| **All LMS endpoints** | **User** | `require_user_role` |
| **All Course Content endpoints** | **User** | `require_user_role` |

## CMS Endpoints (Admin Only)

All CMS endpoints require admin role:

- `GET /api/v1/plugins` - List plugins
- `POST /api/v1/contents` - Create content
- `GET /api/v1/contents/{id}` - Get content
- `PUT /api/v1/contents/{id}` - Update content
- `DELETE /api/v1/contents/{id}` - Delete content
- `GET /api/v1/contents` - List content

**Error Response** (403 Forbidden):
```json
{
  "detail": {
    "status": 403,
    "developerMessage": "Admin role required to access this endpoint",
    "userMessage": "You don't have permission to access this resource",
    "errorCode": "INSUFFICIENT_PERMISSIONS"
  }
}
```

## LMS Endpoints (User Role Required)

All LMS endpoints require user role (any authenticated user):

- `POST /api/v1/courses` - Create course
- `GET /api/v1/courses/{id}` - Get course
- `PUT /api/v1/courses/{id}` - Update course
- `DELETE /api/v1/courses/{id}` - Delete course
- `GET /api/v1/courses` - List courses
- `POST /api/v1/enrollments` - Enroll in course
- `DELETE /api/v1/enrollments/{id}` - Unenroll from course
- `GET /api/v1/my-courses` - Get my courses
- All course content management endpoints

## How It Works

### Step 1: User Authentication
User logs in and receives a JWT token:
```bash
POST /api/v1/tokens
→ Returns: {"access_token": "...", "token_type": "bearer"}
```

### Step 2: Token Validation
When accessing a protected endpoint, the token is validated:
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validates token and extracts username
    return username
```

### Step 3: Role Retrieval
The system fetches user roles from database:
```python
async def get_current_user_with_roles(...):
    # Gets user and their roles
    roles = db.query(Role).filter(Role.user_id == user.id).all()
    return username, [role.role for role in roles]
```

### Step 4: Role Check
The appropriate dependency checks the required role:
```python
async def require_admin_role(...):
    if RoleType.admin not in roles:
        raise HTTPException(403, "Admin role required")
    return username
```

## Usage Examples

### Example 1: Admin Accessing CMS

```bash
# 1. Login as admin user
POST /api/v1/tokens
{
  "username": "admin@example.com",
  "password": "password"
}
→ Returns token

# 2. Access CMS endpoint with admin token
GET /api/v1/contents
Authorization: Bearer <admin_token>
→ 200 OK (Admin has access)
```

### Example 2: Regular User Accessing CMS (Should Fail)

```bash
# 1. Login as regular user
POST /api/v1/tokens
{
  "username": "user@example.com",
  "password": "password"
}
→ Returns token

# 2. Try to access CMS endpoint
GET /api/v1/contents
Authorization: Bearer <user_token>
→ 403 Forbidden (User doesn't have admin role)
```

### Example 3: Regular User Accessing LMS (Should Succeed)

```bash
# 1. Login as regular user
POST /api/v1/tokens
{
  "username": "user@example.com",
  "password": "password"
}
→ Returns token

# 2. Access LMS endpoint
GET /api/v1/courses
Authorization: Bearer <user_token>
→ 200 OK (User has access)
```

## Assigning Roles

To give a user admin access:

```bash
# Add admin role to user
POST /api/v1/users/{user_id}/roles
Authorization: Bearer <token>
{
  "role": "admin"
}
```

## Default Behavior

- **New Users**: Automatically get `user` role on registration
- **Role Check**: If user has no roles, `require_user_role` will fail
- **Multiple Roles**: Users can have multiple roles (e.g., both `user` and `admin`)

## Security Notes

1. **Token-Based**: All role checks happen server-side after token validation
2. **Database Lookup**: Roles are fetched from database on each request (not cached in token)
3. **Default Role**: All users get `user` role by default, ensuring LMS access
4. **Admin Protection**: CMS endpoints are protected by admin role requirement
5. **Error Messages**: Clear error messages help distinguish between authentication (401) and authorization (403) failures

## Testing Role-Based Access

### Test Admin Access
```bash
# 1. Create admin user
POST /api/v1/users
{"email": "admin@test.com", "password": "password"}

# 2. Add admin role
POST /api/v1/users/{user_id}/roles
{"role": "admin"}

# 3. Login
POST /api/v1/tokens
{"username": "admin@test.com", "password": "password"}

# 4. Access CMS
GET /api/v1/contents
Authorization: Bearer <token>
→ Should work
```

### Test User Access
```bash
# 1. Create regular user (auto-gets 'user' role)
POST /api/v1/users
{"email": "user@test.com", "password": "password"}

# 2. Login
POST /api/v1/tokens
{"username": "user@test.com", "password": "password"}

# 3. Try CMS (should fail)
GET /api/v1/contents
Authorization: Bearer <token>
→ 403 Forbidden

# 4. Access LMS (should work)
GET /api/v1/courses
Authorization: Bearer <token>
→ Should work
```
