# RBAC Middleware Documentation

## Overview

The `RBACMiddleware` automatically enforces role-based access control for API endpoints based on URL path patterns. This eliminates the need to add role-checking dependencies to every endpoint.

## How It Works

The middleware intercepts all requests and:

1. **Checks if path is public** - Skips RBAC for public endpoints (register, login)
2. **Checks if path requires auth only** - Validates token but doesn't check roles
3. **Matches path patterns** - Determines required role based on URL pattern
4. **Validates token** - Extracts and validates JWT token
5. **Checks user roles** - Queries database for user roles
6. **Enforces access** - Allows or denies based on role requirements

## Configuration

### Path to Role Mapping

The middleware uses regex patterns to match paths:

```python
PATH_ROLE_MAPPING = [
    # CMS endpoints require admin role
    (re.compile(r"^/api/v1/plugins"), RoleType.admin),
    (re.compile(r"^/api/v1/contents"), RoleType.admin),
    # LMS endpoints require user role
    (re.compile(r"^/api/v1/courses"), RoleType.user),
    (re.compile(r"^/api/v1/enrollments"), RoleType.user),
    (re.compile(r"^/api/v1/my-courses"), RoleType.user),
]
```

### Public Paths

Paths that don't require authentication:

```python
PUBLIC_PATHS = [
    "/api/v1/users",  # POST - register
    "/api/v1/tokens",  # POST - login
]
```

### Auth-Only Paths

Paths that require authentication but no specific role:

```python
AUTH_ONLY_PATHS = [
    "/api/v1/token-renewals",  # POST - renew token
    "/api/v1/users/me",  # GET - current user info
]
```

## Usage

### Basic Setup

The middleware is already configured in `main.py`:

```python
from app.core.rbac_middleware import RBACMiddleware

app.add_middleware(RBACMiddleware, enabled=True)
```

### Disable Middleware

To disable RBAC middleware (for testing or development):

```python
app.add_middleware(RBACMiddleware, enabled=False)
```

### Access User Info in Endpoints

The middleware stores user information in `request.state`:

```python
from fastapi import Request

@router.get("/example")
async def example_endpoint(request: Request):
    username = request.state.user  # Set by middleware
    user_id = request.state.user_id  # Set by middleware
    user_roles = request.state.user_roles  # Set by middleware
```

Or use helper functions:

```python
from app.core.rbac_helpers import get_user_from_request, get_user_roles_from_request

@router.get("/example")
async def example_endpoint(request: Request):
    username = get_user_from_request(request)
    roles = get_user_roles_from_request(request)
```

## Benefits

### 1. **Automatic Enforcement**
- No need to add `Depends(require_admin_role)` to every CMS endpoint
- No need to add `Depends(require_user_role)` to every LMS endpoint
- RBAC is enforced automatically based on path patterns

### 2. **Centralized Configuration**
- All RBAC rules in one place (`rbac_middleware.py`)
- Easy to update role requirements
- Clear visibility of access control rules

### 3. **Consistent Error Handling**
- Standardized error responses
- Follows White House Web API Standards
- Clear error messages for developers and users

### 4. **Performance**
- Single database query for user and roles
- Results cached in `request.state` for endpoint use
- No redundant role checks

## Current Implementation

### With Middleware (Current)

**Endpoints are simpler** - no role dependencies needed:

```python
# CMS endpoint - middleware automatically enforces admin role
@router.post("/contents")
async def create_content(
    content: ContentCreate,
    _current_user: str = Depends(require_admin_role),  # Still works, but middleware also checks
):
    ...
```

### Without Middleware (Alternative)

You would need dependencies on every endpoint:

```python
# CMS endpoint - manual role check
@router.post("/contents")
async def create_content(
    content: ContentCreate,
    _current_user: str = Depends(require_admin_role),  # Required
):
    ...
```

## Hybrid Approach

You can use both middleware and dependencies:

- **Middleware**: Handles automatic RBAC based on path patterns
- **Dependencies**: Handle fine-grained or conditional role checks

Example:

```python
@router.post("/contents")
async def create_content(
    content: ContentCreate,
    request: Request,  # Access middleware-set user info
    _current_user: str = Depends(require_admin_role),  # Additional check if needed
):
    # Middleware already checked admin role
    # Dependency provides additional validation
    username = request.state.user
    ...
```

## Adding New Path Patterns

To add RBAC for new endpoints:

1. **Add path pattern** to `PATH_ROLE_MAPPING`:

```python
PATH_ROLE_MAPPING = [
    # ... existing patterns ...
    (re.compile(r"^/api/v1/notifications"), RoleType.user),  # New pattern
]
```

2. **Or add to public/auth-only lists** if no role required:

```python
PUBLIC_PATHS = [
    # ... existing paths ...
    "/api/v1/public-endpoint",
]
```

## Request State

The middleware sets the following in `request.state`:

- `request.state.user` - Username (str)
- `request.state.user_id` - User ID (str)
- `request.state.user_roles` - List of user roles (List[RoleType])

These are available in all endpoint handlers after middleware runs.

## Error Responses

### 401 Unauthorized (No Token)
```json
{
  "detail": {
    "status": 401,
    "developerMessage": "Authentication required",
    "userMessage": "Please provide a valid authentication token",
    "errorCode": "AUTHENTICATION_REQUIRED"
  }
}
```

### 401 Unauthorized (Invalid Token)
```json
{
  "detail": {
    "status": 401,
    "developerMessage": "Invalid or expired token",
    "userMessage": "Authentication failed",
    "errorCode": "INVALID_TOKEN"
  }
}
```

### 403 Forbidden (Insufficient Permissions)
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

## Testing

### Test Admin Access
```bash
# 1. Create admin user and add role
POST /api/v1/users
POST /api/v1/users/{id}/roles {"role": "admin"}

# 2. Login
POST /api/v1/tokens

# 3. Access CMS (middleware checks admin role)
GET /api/v1/contents
Authorization: Bearer <admin_token>
→ 200 OK ✅
```

### Test User Access
```bash
# 1. Create regular user (auto-gets 'user' role)
POST /api/v1/users

# 2. Login
POST /api/v1/tokens

# 3. Try CMS (middleware blocks - no admin role)
GET /api/v1/contents
Authorization: Bearer <user_token>
→ 403 Forbidden ❌

# 4. Access LMS (middleware allows - has user role)
GET /api/v1/courses
Authorization: Bearer <user_token>
→ 200 OK ✅
```

## Migration from Dependencies

If you want to simplify endpoints by removing role dependencies:

**Before (with dependencies):**
```python
@router.post("/contents")
async def create_content(
    content: ContentCreate,
    _current_user: str = Depends(require_admin_role),
):
    ...
```

**After (middleware only):**
```python
@router.post("/contents")
async def create_content(
    content: ContentCreate,
    request: Request,  # Optional: access user info
):
    # Middleware already enforced admin role
    username = request.state.user  # If needed
    ...
```

## Best Practices

1. **Keep middleware enabled** in production
2. **Use path patterns** for automatic RBAC
3. **Use dependencies** for fine-grained or conditional checks
4. **Access user info** via `request.state` when needed
5. **Document exceptions** if paths don't follow standard patterns

## Troubleshooting

### Middleware Not Working

1. Check middleware is added in `main.py`
2. Verify `enabled=True` is set
3. Check path patterns match your endpoints
4. Verify route tags are set correctly

### 403 Errors When Should Work

1. Verify user has required role in database
2. Check path pattern matches endpoint URL
3. Verify token is valid and not expired
4. Check user is active (`is_active=True`)

### 401 Errors

1. Verify token is in `Authorization: Bearer <token>` format
2. Check token is not expired
3. Verify user exists in database
4. Check token secret key matches
