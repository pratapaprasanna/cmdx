# Database Schema Documentation

## Overview

This document describes the database schema for the CMS-LMS system. The schema is defined using SQLAlchemy ORM models and managed through Alembic migrations.

## Schema Location

### 1. Model Definitions
**Location**: `app/db/models.py`

This is the **source of truth** for the database schema. All table structures are defined here using SQLAlchemy models.

### 2. Migrations
**Location**: `alembic/versions/`

Alembic migrations create and modify the actual database tables. The initial migration is:
- `678a65077628_initial_migration_with_uuid.py` - Creates initial tables (users, courses, content, enrollments)
- `a2b1d923382a_add_role_model.py` - Adds roles table

## Course Schema

### Table: `courses`

The courses table stores Learning Management System course data.

**SQLAlchemy Model**: `app/db/models.py` (lines 74-88)

```python
class Course(Base):
    __tablename__ = "courses"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    instructor = Column(String, nullable=False)
    modules = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Database Schema** (from migration):

```sql
CREATE TABLE courses (
    id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    instructor VARCHAR NOT NULL,
    modules JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);

CREATE INDEX ix_courses_id ON courses (id);
```

### Column Details

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | VARCHAR | NO | - | Primary key, course identifier |
| `title` | VARCHAR | NO | - | Course title |
| `description` | TEXT | NO | - | Course description |
| `instructor` | VARCHAR | NO | - | Instructor name/ID |
| `modules` | JSON | YES | `[]` | Course modules with content references |
| `created_at` | TIMESTAMP WITH TIME ZONE | YES | `now()` | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | YES | - | Last update timestamp |

### Modules JSON Structure

The `modules` column stores a JSON array with the following structure:

```json
[
  {
    "id": "module_1",
    "title": "Introduction",
    "description": "Course introduction",
    "order": 1,
    "content_items": [
      {
        "content_id": "content_123",
        "plugin": "database",
        "type": "lesson",
        "order": 1,
        "metadata": {}
      }
    ]
  }
]
```

## Related Tables

### Table: `user_course_enrollment`

Association table for many-to-many relationship between users and courses.

**Location**: `app/db/models.py` (lines 13-19)

```sql
CREATE TABLE user_course_enrollment (
    user_id VARCHAR NOT NULL,
    course_id VARCHAR NOT NULL,
    PRIMARY KEY (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

## Complete Schema Overview

### Users Table
- Stores user accounts and authentication data
- Related to: courses (via enrollments), roles

### Courses Table
- Stores course information and module structure
- Related to: users (via enrollments)

### Content Table
- Stores CMS content metadata (actual content may be in plugins)
- Used by: courses (referenced in modules)

### Roles Table
- Stores user role assignments
- Related to: users

### Enrollment Table
- Junction table for user-course enrollments
- Related to: users, courses

## Migration Commands

### View Current Schema
```bash
# Check current migration status
alembic current

# View migration history
alembic history
```

### Apply Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>
```

### Create New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

## Schema Evolution

### Initial Schema (Revision: 678a65077628)
- Created: 2026-01-11
- Tables: users, courses, content, user_course_enrollment

### Role Model (Revision: a2b1d923382a)
- Created: After initial migration
- Tables: roles

### Future Migrations
When modifying the Course model (e.g., adding new columns), create a new migration:

```bash
alembic revision --autogenerate -m "add_column_to_courses"
```

## Notes

1. **Modules as JSON**: The `modules` column uses JSON type to store flexible module structures. This allows:
   - Dynamic module structure
   - Content references from multiple CMS plugins
   - No need for separate module/content tables

2. **String IDs**: All IDs are VARCHAR/String type, allowing:
   - UUIDs
   - Custom identifiers
   - Plugin-specific content IDs

3. **Timezone-aware Timestamps**: All datetime columns use `TIMESTAMP WITH TIME ZONE` for proper timezone handling.

4. **Indexes**: Primary keys are automatically indexed. Additional indexes can be added for frequently queried columns.

## Example Queries

### Get Course with Modules
```sql
SELECT id, title, modules 
FROM courses 
WHERE id = 'course_123';
```

### Get Enrolled Users for Course
```sql
SELECT u.id, u.username, u.email
FROM users u
JOIN user_course_enrollment e ON u.id = e.user_id
WHERE e.course_id = 'course_123';
```

### Get Courses for User
```sql
SELECT c.id, c.title, c.description
FROM courses c
JOIN user_course_enrollment e ON c.id = e.course_id
WHERE e.user_id = 'user_123';
```
