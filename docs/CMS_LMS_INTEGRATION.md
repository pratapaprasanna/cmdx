# CMS-LMS Integration Guide

## Overview

This guide explains how to use the integrated CMS (Content Management System) and LMS (Learning Management System) where content from various storage backends (databases, filesystems) can be served in courses.

## Architecture

```
┌─────────────────┐
│   CMS Plugins   │
│  (database, fs) │
└────────┬────────┘
         │
         │ stores content
         │
┌────────▼────────┐
│   CMS Service   │
│  (manages       │
│   content)      │
└────────┬────────┘
         │
         │ references
         │
┌────────▼────────┐
│   LMS Service   │
│  (manages       │
│   courses)      │
└────────┬────────┘
         │
         │ resolves content
         │
┌────────▼────────┐
│ Course Content  │
│   Resolver      │
└─────────────────┘
```

## Workflow

### Step 1: Create Content in CMS

Content can be created using any available plugin (database, filesystem, etc.):

```bash
# Create content in database plugin
curl -X POST "http://localhost:8000/api/v1/contents?plugin=database" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction to Python",
    "body": "Python is a high-level programming language...",
    "metadata": {"type": "lesson", "duration": "10min"}
  }'

# Response includes content_id
{
  "id": "content_abc123",
  "title": "Introduction to Python",
  "body": "Python is a high-level programming language...",
  "plugin": "database",
  ...
}
```

### Step 2: Create Course with Content References

Create a course and reference CMS content in modules:

```bash
curl -X POST "http://localhost:8000/api/v1/courses" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "description": "Learn Python programming",
    "instructor": "John Doe",
    "modules": [{
      "id": "module_1",
      "title": "Getting Started",
      "order": 1,
      "content_items": [{
        "content_id": "content_abc123",
        "plugin": "database",
        "type": "lesson",
        "order": 1
      }]
    }]
  }'
```

### Step 3: Add More Content to Modules

Add additional content to existing modules:

```bash
curl -X POST "http://localhost:8000/api/v1/courses/{course_id}/modules/{module_id}/content" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "content_xyz789",
    "plugin": "filesystem",
    "type": "video",
    "order": 2,
    "metadata": {"duration": "15min"}
  }'
```

### Step 4: Retrieve Course with Resolved Content

Get course with all content fetched from respective plugins:

```bash
curl -X GET "http://localhost:8000/api/v1/courses/{course_id}?resolve_content=true" \
  -H "Authorization: Bearer <token>"
```

Response includes full content:

```json
{
  "id": "course_123",
  "title": "Python Basics",
  "modules": [{
    "id": "module_1",
    "title": "Getting Started",
    "content_items": [{
      "content_id": "content_abc123",
      "plugin": "database",
      "type": "lesson",
      "order": 1,
      "content": {
        "id": "content_abc123",
        "title": "Introduction to Python",
        "body": "Python is a high-level programming language...",
        "metadata": {"type": "lesson", "duration": "10min"}
      },
      "content_resolved": true
    }]
  }]
}
```

## API Endpoints

### Course Content Management

#### Add Content to Module
**POST** `/api/v1/courses/{course_id}/modules/{module_id}/content`

Adds CMS content to a course module. Validates that content exists before adding.

**Request Body:**
```json
{
  "content_id": "string",
  "plugin": "string",
  "type": "string (optional)",
  "order": 0,
  "metadata": {}
}
```

#### Remove Content from Module
**DELETE** `/api/v1/courses/{course_id}/modules/{module_id}/content/{content_id}?plugin={plugin_name}`

Removes content from a module.

#### Validate Module Content
**GET** `/api/v1/courses/{course_id}/modules/{module_id}/content/validate`

Validates that all content references in a module exist.

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "missing_content": []
}
```

### Enhanced Course Endpoints

#### Get Course (with optional content resolution)
**GET** `/api/v1/courses/{course_id}?resolve_content=true`

- `resolve_content=false` (default): Returns course with content references only
- `resolve_content=true`: Fetches and embeds full content from CMS

#### Get My Courses (with optional content resolution)
**GET** `/api/v1/my-courses?resolve_content=true`

Returns enrolled courses with optional content resolution.

## Module Structure

### Module Schema

```json
{
  "id": "string",
  "title": "string",
  "description": "string (optional)",
  "order": 0,
  "content_items": [
    {
      "content_id": "string",
      "plugin": "string",
      "type": "string (optional)",
      "order": 0,
      "metadata": {}
    }
  ]
}
```

### Content Item Schema

- `content_id`: CMS content ID (required)
- `plugin`: Plugin name where content is stored (required)
- `type`: Content type (e.g., "lesson", "video", "quiz") (optional)
- `order`: Display order within module (default: 0)
- `metadata`: Additional metadata (optional)

## Use Cases

### Use Case 1: Multi-Plugin Course

Create a course using content from multiple storage backends:

```json
{
  "modules": [{
    "id": "module_1",
    "title": "Introduction",
    "content_items": [
      {
        "content_id": "lesson_1",
        "plugin": "database",
        "type": "lesson"
      },
      {
        "content_id": "video_1",
        "plugin": "filesystem",
        "type": "video"
      }
    ]
  }]
}
```

### Use Case 2: Content Reuse

Same CMS content used in multiple courses:

```json
// Course 1
{
  "modules": [{
    "content_items": [{
      "content_id": "intro_python",
      "plugin": "database"
    }]
  }]
}

// Course 2
{
  "modules": [{
    "content_items": [{
      "content_id": "intro_python",  // Same content!
      "plugin": "database"
    }]
  }]
}
```

### Use Case 3: Dynamic Content Updates

1. Update content in CMS
2. Content changes automatically reflect in courses (when resolved)
3. No need to update course structure

## Error Handling

### Missing Content

If content is not found when resolving:

```json
{
  "content_id": "missing_content",
  "plugin": "database",
  "content": null,
  "content_resolved": false,
  "error": "Content not found"
}
```

### Invalid Plugin

If plugin doesn't exist:

```json
{
  "detail": {
    "status": 400,
    "developerMessage": "Plugin 'invalid_plugin' not found",
    "userMessage": "Invalid plugin specified"
  }
}
```

## Best Practices

1. **Validate Before Adding**: Use validation endpoint before adding content to modules
2. **Use Consistent Plugins**: Choose appropriate plugin for content type (database for text, filesystem for large files)
3. **Order Content**: Use `order` field to control content display sequence
4. **Metadata**: Store content-specific metadata (duration, difficulty, etc.) in content items
5. **Lazy Resolution**: Only resolve content when needed (use `resolve_content=true` parameter)
6. **Error Handling**: Always check `content_resolved` flag when displaying content

## Future Enhancements

- [ ] Content versioning support
- [ ] Content caching for performance
- [ ] Bulk content operations
- [ ] Content preview endpoints
- [ ] Content dependency management
- [ ] Content analytics
