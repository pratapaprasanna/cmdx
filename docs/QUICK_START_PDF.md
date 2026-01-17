# Quick Start: Creating Content from PDF

## For Your PDF: `/Users/gouthampratapa/Documents/python_basics.pdf`

### Step 1: Install PDF Library

```bash
pip install PyPDF2
```

### Step 2: Run the Import Script

```bash
cd /Users/gouthampratapa/temp/cmdx
python scripts/create_content_from_pdf.py /Users/gouthampratapa/Documents/python_basics.pdf "Python Basics"
```

### Step 3: Get Content ID

The script will output something like:
```
✓ Created content with ID: db_1234567890
```

### Step 4: Use in Course

Once you have the content ID, you can add it to a course module:

```bash
# Add to course module
curl -X POST "http://localhost:8000/api/v1/courses/{course_id}/modules/{module_id}/content" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "db_1234567890",
    "plugin": "database",
    "type": "lesson",
    "order": 1
  }'
```

## Alternative: Manual Creation via API

If you prefer to extract text manually and create via API:

### Step 1: Extract Text from PDF

Use any PDF reader or online tool to extract text, or use Python:

```python
import PyPDF2

with open("/Users/gouthampratapa/Documents/python_basics.pdf", "rb") as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    print(text)  # Copy this text
```

### Step 2: Create Content via API

```bash
curl -X POST "http://localhost:8000/api/v1/contents?plugin=database" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "body": "<paste_extracted_text_here>",
    "metadata": {
      "source": "pdf",
      "file": "python_basics.pdf"
    }
  }'
```

## What You Need

1. **Admin Role**: You need admin role to create CMS content
2. **Authentication Token**: Get token by logging in
3. **PDF File**: The PDF file you want to import

## Full Example Workflow

```bash
# 1. Login as admin
curl -X POST "http://localhost:8000/api/v1/tokens" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password"
# Save the access_token

# 2. Import PDF
python scripts/create_content_from_pdf.py \
  /Users/gouthampratapa/Documents/python_basics.pdf \
  "Python Basics" \
  database

# Output: Content ID: db_abc123

# 3. Create course (if needed)
curl -X POST "http://localhost:8000/api/v1/courses" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Course",
    "description": "Learn Python programming",
    "instructor": "John Doe",
    "modules": [{
      "id": "module_1",
      "title": "Introduction",
      "content_items": []
    }]
  }'
# Save course_id

# 4. Add PDF content to course
curl -X POST "http://localhost:8000/api/v1/courses/{course_id}/modules/module_1/content" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "db_abc123",
    "plugin": "database",
    "type": "lesson",
    "order": 1
  }'

# 5. View course with content
curl "http://localhost:8000/api/v1/courses/{course_id}?resolve_content=true" \
  -H "Authorization: Bearer <token>"
```

## Troubleshooting

**"PyPDF2 not installed"**
```bash
pip install PyPDF2
```

**"No text extracted"**
- PDF might be image-based (scanned). Use OCR first.
- Check if PDF is encrypted or corrupted.

**"403 Forbidden"**
- You need admin role to create CMS content
- Add admin role: `POST /api/v1/users/{user_id}/roles {"role": "admin"}`

**"Database connection failed"**
- Ensure database is running
- Check `.env` file for `DATABASE_URL`
