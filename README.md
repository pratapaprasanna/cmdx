# CMS API Server

A FastAPI-based Content Management System with Authentication, CMS, and Learning Management System (LMS) services.

## Features

- **Authentication Service**: User registration, login, and JWT-based authentication
- **CMS Service**: Content management with pluggable storage backends (PostgreSQL database and filesystem)
- **LMS Service**: Learning Management System for courses and enrollments
- **Plugin System**: Extensible plugin architecture for CMS storage backends
- **PostgreSQL Integration**: Full PostgreSQL database support with SQLAlchemy ORM
- **Comprehensive Tests**: Full test coverage for all services
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **API Standards Compliance**: Follows [White House Web API Standards](https://apistylebook.com/design/guidelines/white-house-web-api-standards)

## Project Structure

```
cmdx/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py      # Authentication endpoints
│   │       │   ├── cms.py        # CMS endpoints
│   │       │   └── lms.py        # LMS endpoints
│   │       └── router.py         # API router
│   ├── core/
│   │   ├── config.py            # Application configuration
│   │   ├── security.py          # Security utilities (JWT, password hashing)
│   │   └── exceptions.py        # Standardized error handling
│   ├── db/
│   │   ├── base.py              # Database connection and session
│   │   └── models.py            # SQLAlchemy models
│   ├── schemas/
│   │   ├── auth.py              # Authentication schemas
│   │   ├── cms.py               # CMS schemas
│   │   └── lms.py               # LMS schemas
│   └── services/
│       ├── auth/
│       │   └── auth_service.py  # Authentication service
│       ├── cms/
│       │   ├── cms_service.py   # CMS service
│       │   └── plugins/
│       │       ├── base.py      # Base plugin interface
│       │       ├── registry.py  # Plugin registry
│       │       ├── database_plugin.py    # PostgreSQL plugin
│       │       └── filesystem_plugin.py  # Filesystem plugin
│       └── lms/
│           └── lms_service.py   # LMS service
├── alembic/                     # Database migrations
├── tests/                       # Test suite
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cmdx
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL database URL and secret key
   ```

5. **Set up the database**:
   ```bash
   # Create PostgreSQL database
   createdb cmdx_db
   
   # Run migrations
   alembic upgrade head
   ```

## Configuration

Edit the `.env` file with your configuration:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/cmdx_db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
API_V1_PREFIX=/api/v1
```

## Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /users` - Register a new user (automatically assigns "user" role)
  ```bash
  curl -X POST "http://localhost:8000/api/v1/users" \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "securepassword"}'
  ```

- `POST /tokens` - Login and get access token
  ```bash
  curl -X POST "http://localhost:8000/api/v1/tokens" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test@example.com&password=securepassword"
  ```

- `POST /token-renewals` - Renew access token
  ```bash
  curl -X POST "http://localhost:8000/api/v1/token-renewals" \
    -H "Authorization: Bearer <your_access_token>"
  ```

- `GET /users/me` - Get current user information
  ```bash
  curl -X GET "http://localhost:8000/api/v1/users/me" \
    -H "Authorization: Bearer <your_access_token>"
  ```

### User Roles

- `GET /users/{user_id}/roles` - Get all roles for a user (user_id can be UUID or username)
  ```bash
  curl -X GET "http://localhost:8000/api/v1/users/{user_id}/roles" \
    -H "Authorization: Bearer <your_access_token>"
  ```

- `POST /users/{user_id}/roles` - Add a role to a user
  ```bash
  curl -X POST "http://localhost:8000/api/v1/users/{user_id}/roles" \
    -H "Authorization: Bearer <your_access_token>" \
    -H "Content-Type: application/json" \
    -d '{"role": "admin"}'
  ```

**Available Roles:**
- `user` - Default role assigned to all new users
- `admin` - Administrator role
- `developer` - Developer role

**Note:** If a user has no roles, the default "user" role is automatically assigned when querying roles.

### CMS

- `GET /plugins` - List available storage plugins
- `POST /contents` - Create new content
- `GET /contents/{content_id}` - Get content by ID
- `PUT /contents/{content_id}` - Update content
- `DELETE /contents/{content_id}` - Delete content
- `GET /contents` - List all content (with pagination)

**Query Parameters:**
- `plugin` - Specify which plugin to use (database or filesystem)

### LMS

- `POST /courses` - Create a new course
- `GET /courses/{course_id}` - Get course by ID
- `PUT /courses/{course_id}` - Update course
- `DELETE /courses/{course_id}` - Delete course
- `GET /courses` - List all courses (with pagination)
- `POST /enrollments` - Enroll a user in a course
- `DELETE /enrollments/{course_id}` - Unenroll from a course
- `GET /my-courses` - Get current user's enrolled courses

## CMS Plugin System

The CMS service supports a plugin-based architecture for different storage backends:

### Available Plugins

1. **Database Plugin** (default): Stores content in PostgreSQL database
2. **Filesystem Plugin**: Stores content as JSON files on the filesystem

### Using Plugins

Specify the plugin when making CMS requests:

```bash
# Use database plugin (default)
POST /api/v1/contents?plugin=database

# Use filesystem plugin
POST /api/v1/contents?plugin=filesystem
```

### Creating Custom Plugins

To create a custom plugin, inherit from `BasePlugin` and implement all abstract methods:

```python
from app.services.cms.plugins.base import BasePlugin

class MyCustomPlugin(BasePlugin):
    async def connect(self) -> bool:
        # Initialize connection
        pass
    
    async def get_content(self, content_id: str):
        # Implement content retrieval
        pass
    
    # ... implement other required methods
```

Then register it in the plugin registry.

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Database Migrations

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Development

### Code Structure

- **Services**: Business logic and data access
- **Endpoints**: API route handlers
- **Schemas**: Pydantic models for request/response validation
- **Models**: SQLAlchemy database models
- **Plugins**: Extensible storage backends for CMS

### Adding New Features

1. Create database models in `app/db/models.py`
2. Create schemas in `app/schemas/`
3. Implement service logic in `app/services/`
4. Create API endpoints in `app/api/v1/endpoints/`
5. Add tests in `tests/`
6. Update documentation

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Token expiration configured via `ACCESS_TOKEN_EXPIRE_MINUTES`
- All endpoints (except auth) require authentication

## License

This project is open source and available under the MIT License.

## API Standards

This project follows the **White House Web API Standards** as defined at https://apistylebook.com/design/guidelines/white-house-web-api-standards

Key principles:
- RESTful URL design (plural nouns, no verbs in paths)
- Proper HTTP method usage (GET, POST, PUT, DELETE)
- Standardized error responses
- API versioning (`/api/v1/...`)
- Pagination and filtering support

See `.cursorrules` for detailed coding standards and requirements for all new endpoints.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Before submitting:**
- Ensure all new endpoints follow the White House Web API Standards (see `.cursorrules`)
- Add tests for new functionality
- Update API documentation
- Follow the existing code style and structure
