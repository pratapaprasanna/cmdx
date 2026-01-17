"""
Utility script to extract content from PDF and create CMS content
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import PyPDF2
except ImportError:
    print("ERROR: PyPDF2 is not installed.")
    print("Please install it using: pip install PyPDF2")
    print("Or install all requirements: pip install -r requirements.txt")
    sys.exit(1)

from app.services.cms.cms_service import CMSService


def extract_text_from_pdf(pdf_path: str) -> tuple[str, dict]:
    """
    Extract text and metadata from PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple of (text_content, metadata_dict)
    """
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                    "producer": pdf_reader.metadata.get("/Producer", ""),
                    "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")),
                    "modification_date": str(pdf_reader.metadata.get("/ModDate", "")),
                }
            
            # Extract text from all pages
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                text_content += f"\n\n--- Page {page_num} ---\n\n"
                text_content += page_text
            
            # Add PDF info to metadata
            metadata.update({
                "source": "pdf",
                "source_file": os.path.basename(pdf_path),
                "total_pages": len(pdf_reader.pages),
                "file_size": os.path.getsize(pdf_path),
            })
            
            return text_content.strip(), metadata
            
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}") from e


def split_content_by_pages(text: str, metadata: dict, max_chunk_size: int = 50000) -> list[dict]:
    """
    Split large PDF content into smaller chunks if needed
    
    Args:
        text: Full text content
        metadata: Content metadata
        max_chunk_size: Maximum characters per chunk
        
    Returns:
        List of content dictionaries
    """
    if len(text) <= max_chunk_size:
        return [{"text": text, "metadata": metadata}]
    
    # Split by pages
    chunks = []
    pages = text.split("--- Page")
    
    current_chunk = ""
    chunk_num = 1
    
    for page in pages:
        if not page.strip():
            continue
            
        if len(current_chunk) + len(page) > max_chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {**metadata, "chunk": chunk_num, "total_chunks": None}
            })
            current_chunk = page
            chunk_num += 1
        else:
            current_chunk += "\n--- Page" + page if current_chunk else page
    
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": {**metadata, "chunk": chunk_num, "total_chunks": chunk_num}
        })
    
    # Update total_chunks for all chunks
    for chunk in chunks:
        if "total_chunks" in chunk["metadata"] and chunk["metadata"]["total_chunks"] is None:
            chunk["metadata"]["total_chunks"] = len(chunks)
    
    return chunks


async def create_content_from_pdf(
    pdf_path: str,
    title: Optional[str] = None,
    plugin: str = "database",
    split_large: bool = True,
    max_chunk_size: int = 50000,
) -> list[dict]:
    """
    Extract content from PDF and create CMS content
    
    Args:
        pdf_path: Path to PDF file
        title: Custom title (if None, uses PDF metadata or filename)
        plugin: CMS plugin to use ("database" or "filesystem")
        split_large: Whether to split large PDFs into multiple content items
        max_chunk_size: Maximum characters per content item if splitting
        
    Returns:
        List of created content items
    """
    # Extract text from PDF
    print(f"Extracting text from PDF: {pdf_path}")
    text, metadata = extract_text_from_pdf(pdf_path)
    
    if not text:
        raise ValueError("No text content extracted from PDF")
    
    # Determine title
    if not title:
        title = metadata.get("title") or os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Split content if needed
    if split_large and len(text) > max_chunk_size:
        print(f"PDF is large ({len(text)} chars), splitting into chunks...")
        chunks = split_content_by_pages(text, metadata, max_chunk_size)
    else:
        chunks = [{"text": text, "metadata": metadata}]
    
    # Create content items
    cms_service = CMSService()
    created_contents = []
    
    for idx, chunk in enumerate(chunks, start=1):
        chunk_title = title if len(chunks) == 1 else f"{title} - Part {idx}"
        
        content_data = {
            "title": chunk_title,
            "body": chunk["text"],
            "metadata": {
                **chunk["metadata"],
                "content_type": "pdf_extract",
                "original_title": title,
            }
        }
        
        print(f"Creating content: {chunk_title} ({len(chunk['text'])} chars)")
        result = await cms_service.create_content(content_data, plugin_name=plugin)
        created_contents.append(result)
        print(f"✓ Created content with ID: {result['id']}")
    
    return created_contents


async def main():
    """Main function to run the script"""
    if len(sys.argv) < 2:
        print("Usage: python create_content_from_pdf.py <pdf_path> [title] [plugin]")
        print("\nExample:")
        print("  python create_content_from_pdf.py /path/to/file.pdf")
        print("  python create_content_from_pdf.py /path/to/file.pdf 'Python Basics' database")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    plugin = sys.argv[3] if len(sys.argv) > 3 else "database"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    try:
        contents = await create_content_from_pdf(
            pdf_path=pdf_path,
            title=title,
            plugin=plugin,
        )
        
        print(f"\n✓ Successfully created {len(contents)} content item(s)")
        print("\nCreated content IDs:")
        for content in contents:
            print(f"  - {content['id']}: {content['title']}")
        
        print("\nYou can now use these content IDs in course modules!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
