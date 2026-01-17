# System Architecture: CMS-LMS Integration

## Overview

This system integrates a **Content Management System (CMS)** with a **Learning Management System (LMS)** where:
- CMS stores content in various backends (databases, filesystems) via plugins
- LMS serves courses that reference and display CMS content
- Content can come from multiple sources (different plugins) within a single course

## Architecture Components

### 1. CMS Plugin System

**Purpose**: Abstract content storage to support multiple backends

**Current Plugins**:
- `database_plugin`: Stores content in PostgreSQL
- `filesystem_plugin`: Stores content as JSON files

**Plugin Interface** (`BasePlugin`):
- `get_content(content_id)` - Retrieve content by ID
- `create_content(content_data)` - Create new content
- `update_content(content_id, content_data)` - Update content
- `delete_content(content_id)` - Delete content
- `list_content(limit, offset)` - List all content
- `search_content(query)` - Search content

### 2. Course Module Structure

**Current State**: Modules are stored as JSON arrays in the Course model

**Proposed Structure**:
```json
{
  "modules": [
    {
      "id": "module_1",
      "title": "Introduction",
      "order": 1,
      "content_items": [
        {
          "content_id": "content_123",
          "plugin": "database",
          "type": "lesson",
          "order": 1
        },
        {
          "content_id": "content_456",
          "plugin": "filesystem",
          "type": "video",
          "order": 2
        }
      ]
    }
  ]
}
```

### 3. Content Resolution Flow

```
Course Request
    ↓
Get Course from DB
    ↓
Extract Module Content References
    ↓
For each content item:
    ├─→ Get plugin from registry
    ├─→ Fetch content from plugin
    └─→ Resolve content
    ↓
Return Course with Resolved Content
```

### 4. Integration Points

#### A. Course Creation/Update
- Allow specifying CMS content IDs when creating modules
- Support content from different plugins in same course
- Validate content exists before adding to course

#### B. Course Retrieval
- Resolve all content references when fetching course
- Return course with full content embedded
- Handle missing content gracefully

#### C. Content Management
- Endpoints to add/remove content from course modules
- Support for reordering content within modules
- Bulk operations for content management

## Data Flow

### Creating a Course with Content

1. **Create Content in CMS** (via any plugin):
   ```bash
   POST /api/v1/contents?plugin=database
   {
     "title": "Lesson 1: Introduction",
     "body": "Welcome to the course...",
     "metadata": {"type": "lesson"}
   }
   ```

2. **Create Course with Content Reference**:
   ```bash
   POST /api/v1/courses
   {
     "title": "Python Basics",
     "description": "Learn Python",
     "instructor": "John Doe",
     "modules": [{
       "id": "module_1",
       "title": "Getting Started",
       "content_items": [{
         "content_id": "content_123",
         "plugin": "database"
       }]
     }]
   }
   ```

3. **Retrieve Course with Resolved Content**:
   ```bash
   GET /api/v1/courses/{course_id}?resolve_content=true
   ```
   Returns course with all content fetched from respective plugins.

## Implementation Plan

### Phase 1: Module Structure Enhancement
- [x] Define module schema with content references
- [ ] Update Course model validation
- [ ] Create module management schemas

### Phase 2: Content Resolution Service
- [ ] Create `CourseContentResolver` service
- [ ] Implement content fetching from multiple plugins
- [ ] Add error handling for missing content

### Phase 3: API Endpoints
- [ ] Add endpoint to get course with resolved content
- [ ] Add endpoint to add content to course module
- [ ] Add endpoint to remove content from module
- [ ] Add endpoint to reorder module content

### Phase 4: Advanced Features
- [ ] Content caching for performance
- [ ] Content versioning support
- [ ] Content preview endpoints
- [ ] Bulk content operations

## Benefits

1. **Flexibility**: Mix content from different storage backends
2. **Scalability**: Add new storage backends via plugins
3. **Separation of Concerns**: CMS handles storage, LMS handles delivery
4. **Reusability**: Same content can be used in multiple courses
5. **Performance**: Lazy loading of content when needed

## Example Use Cases

### Use Case 1: Multi-Source Course
A course uses:
- Database plugin for text lessons
- Filesystem plugin for large video files
- Future S3 plugin for media assets

### Use Case 2: Content Reuse
Same CMS content (e.g., "Introduction to Python") used in:
- "Python Basics" course
- "Advanced Python" course
- "Python for Data Science" course

### Use Case 3: Dynamic Content
Content can be updated in CMS, and changes automatically reflect in courses (when resolved).
