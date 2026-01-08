# Setup Guide

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd cmdx
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Create database
createdb cmdx_db

# Or using psql:
psql -U postgres
CREATE DATABASE cmdx_db;
\q
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/cmdx_db
SECRET_KEY=your-very-secure-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
API_V1_PREFIX=/api/v1
```

**Important**: Replace `username` and `password` with your PostgreSQL credentials, and change `SECRET_KEY` to a secure random string.

### 6. Run Database Migrations

```bash
# Create initial migration (if needed)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

Alternatively, you can initialize the database directly:

```bash
python scripts/init_db.py
```

### 7. Run the Server

```bash
# Development mode
uvicorn main:app --reload

# Or using the Makefile
make run
```

The server will start at `http://localhost:8000`

### 8. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Test

1. Register a user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword"
  }'
```

2. Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

3. Use the token to access protected endpoints:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check database credentials in `.env`
- Ensure database exists: `psql -l | grep cmdx_db`

### Import Errors

- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip list`
- Check Python path: `python -c "import sys; print(sys.path)"`

### Migration Issues

- Reset database: `alembic downgrade base && alembic upgrade head`
- Check migration status: `alembic current`
- View migration history: `alembic history`

## Production Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Use a strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
5. Set up proper database connection pooling
6. Enable HTTPS
7. Set up logging and monitoring

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

