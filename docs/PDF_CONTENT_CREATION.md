# Creating CMS Content from PDF Files

## Overview

This guide explains how to extract content from PDF files and create CMS content items that can be used in LMS courses.

## Quick Start

### Step 1: Install Dependencies

```bash
pip install PyPDF2
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Run the PDF Import Script

```bash
python scripts/create_content_from_pdf.py /Users/gouthampratapa/Documents/python_basics.pdf
```

### Step 3: Use Content in Courses

After creating content, use the returned `content_id` in course modules.

## Script Usage

### Basic Usage

```bash
python scripts/create_content_from_pdf.py <pdf_path>
```

**Example:**
```bash
python scripts/create_content_from_pdf.py /Users/gouthampratapa/Documents/python_basics.pdf
```

### With Custom Title

```bash
python scripts/create_content_from_pdf.py <pdf_path> "Custom Title"
```

**Example:**
```bash
python scripts/create_content_from_pdf.py /Users/gouthampratapa/Documents/python_basics.pdf "Python Programming Basics"
```

### With Plugin Selection

```bash
python scripts/create_content_from_pdf.py <pdf_path> "Title" <plugin>
```

**Example:**
```bash
# Store in database
python scripts/create_content_from_pdf.py /path/to/file.pdf "Title" database

# Store in filesystem
python scripts/create_content_from_pdf.py /path/to/file.pdf "Title" filesystem
```

## What the Script Does

1. **Extracts Text**: Reads all pages from the PDF and extracts text content
2. **Extracts Metadata**: Gets PDF metadata (title, author, creation date, etc.)
3. **Splits Large PDFs**: If PDF is very large (>50,000 chars), splits into multiple content items
4. **Creates CMS Content**: Creates content items via CMS service
5. **Returns Content IDs**: Provides content IDs for use in courses

## Output Example

```
Extracting text from PDF: /Users/gouthampratapa/Documents/python_basics.pdf
Creating content: Python Basics (45230 chars)
✓ Created content with ID: db_1234567890

✓ Successfully created 1 content item(s)

Created content IDs:
  - db_1234567890: Python Basics

You can now use these content IDs in course modules!
```

## Using Content in Courses

After creating content, add it to a course module:

```bash
# 1. Create course (if not exists)
POST /api/v1/courses
{
  "title": "Python Course",
  "description": "Learn Python",
  "instructor": "John Doe",
  "modules": [{
    "id": "module_1",
    "title": "Introduction",
    "content_items": []
  }]
}

# 2. Add PDF content to module
POST /api/v1/courses/{course_id}/modules/module_1/content
{
  "content_id": "db_1234567890",  # From script output
  "plugin": "database",
  "type": "lesson",
  "order": 1,
  "metadata": {
    "source": "pdf",
    "original_file": "python_basics.pdf"
  }
}
```

## Alternative: Manual API Creation

You can also create content manually via API:

### Step 1: Extract PDF Text (Manual)

Use a PDF reader or online tool to extract text, then:

### Step 2: Create Content via API

```bash
curl -X POST "http://localhost:8000/api/v1/contents?plugin=database" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "body": "<extracted_text_from_pdf>",
    "metadata": {
      "source": "pdf",
      "file": "python_basics.pdf",
      "pages": 50
    }
  }'
```

## Content Structure

The script creates content with:

- **title**: PDF title (from metadata) or filename
- **body**: Extracted text from all PDF pages
- **metadata**: 
  - PDF metadata (author, creation date, etc.)
  - Source information (source: "pdf", source_file, total_pages)
  - Content type ("pdf_extract")

## Large PDF Handling

If a PDF is very large (>50,000 characters), the script automatically:

1. Splits content by pages
2. Creates multiple content items (Part 1, Part 2, etc.)
3. Links them via metadata (chunk number, total chunks)

**Example:**
```
Creating content: Python Basics - Part 1 (50000 chars)
Creating content: Python Basics - Part 2 (45230 chars)
```

You can then add all parts to a course module in order.

## Metadata Extracted

The script extracts the following PDF metadata:

- Title
- Author
- Subject
- Creator
- Producer
- Creation Date
- Modification Date
- Total Pages
- File Size

## Troubleshooting

### Error: "PyPDF2 not installed"

```bash
pip install PyPDF2
```

### Error: "No text content extracted"

- PDF might be image-based (scanned). Use OCR tools first.
- PDF might be encrypted. Decrypt first.
- PDF might be corrupted. Verify file integrity.

### Error: "Database connection failed"

- Ensure database is running
- Check `DATABASE_URL` in `.env` file
- Verify database credentials

### Large PDF Performance

For very large PDFs (>100 pages):
- Consider splitting manually
- Use filesystem plugin for better performance
- Process in batches

## Advanced: Custom Extraction

You can modify the script to:

1. **Extract specific pages**:
```python
# Extract only pages 1-10
for page_num in range(1, 11):
    page = pdf_reader.pages[page_num - 1]
    text += page.extract_text()
```

2. **Extract images**:
```python
# Extract images from PDF
for page in pdf_reader.pages:
    if "/XObject" in page["/Resources"]:
        # Process images
        pass
```

3. **Custom metadata**:
```python
metadata = {
    "custom_field": "value",
    "category": "programming",
    "difficulty": "beginner",
}
```

## Integration with Courses

After creating content from PDF:

1. **Get content ID** from script output
2. **Create course** with modules
3. **Add content to module** using content ID
4. **Retrieve course** with `resolve_content=true` to see full content

## Example Workflow

```bash
# 1. Import PDF
python scripts/create_content_from_pdf.py python_basics.pdf "Python Basics"

# Output: Content ID: db_abc123

# 2. Create course
curl -X POST "http://localhost:8000/api/v1/courses" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "title": "Python Course",
    "modules": [{
      "id": "intro",
      "content_items": [{
        "content_id": "db_abc123",
        "plugin": "database"
      }]
    }]
  }'

# 3. View course with content
curl "http://localhost:8000/api/v1/courses/{course_id}?resolve_content=true" \
  -H "Authorization: Bearer <token>"
```

## Best Practices

1. **Use descriptive titles**: Make content easy to find
2. **Add metadata**: Include source file, page count, etc.
3. **Split large PDFs**: Keep content items manageable
4. **Use appropriate plugin**: Database for text, filesystem for large files
5. **Verify extraction**: Check that text was extracted correctly
6. **Organize by topic**: Create separate content items for different topics
