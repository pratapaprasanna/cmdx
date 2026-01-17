"""
PDF utility functions for validation and processing
"""
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None  # type: ignore[assignment]


class PDFValidationError(Exception):
    """Custom exception for PDF validation errors"""
    pass


def validate_pdf_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if a file is a valid, non-corrupt, non-password-protected PDF
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if PDF is valid, False otherwise
        - error_message: Error description if invalid, None if valid
        
    Raises:
        PDFValidationError: If file doesn't exist or can't be read
    """
    if PyPDF2 is None:
        raise PDFValidationError("PyPDF2 is not installed. Install it with: pip install PyPDF2")
    
    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    # Check if it's a file (not directory)
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"
    
    # Check file extension
    if not file_path.lower().endswith('.pdf'):
        return False, f"File is not a PDF: {file_path}"
    
    # Check file size (must be > 0)
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return False, "PDF file is empty"
    
    try:
        # Try to read and validate PDF
        with open(file_path, "rb") as file:
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted (password protected)
                if pdf_reader.is_encrypted:
                    return False, "PDF is password protected"
                
                # Try to access first page to check if corrupt
                if len(pdf_reader.pages) == 0:
                    return False, "PDF has no pages"
                
                # Try to extract text from first page to verify it's readable
                try:
                    first_page = pdf_reader.pages[0]
                    _ = first_page.extract_text()  # Try to extract text
                except Exception as e:
                    return False, f"PDF appears to be corrupt: {str(e)}"
                
                # PDF is valid
                return True, None
                
            except PyPDF2.errors.PdfReadError as e:
                return False, f"PDF is corrupt or invalid: {str(e)}"
            except Exception as e:
                return False, f"Error reading PDF: {str(e)}"
                
    except PermissionError:
        return False, f"Permission denied: {file_path}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def _parse_pdf_date(pdf_date_str: str) -> Optional[int]:
    """
    Parse PDF date string to epoch timestamp
    
    PDF date format: D:YYYYMMDDHHmmSSOHH'mm'
    Example: D:20260117132248+00'00'
    
    Returns:
        Epoch timestamp in seconds, or None if parsing fails
    """
    if not pdf_date_str or pdf_date_str == "(unspecified)":
        return None
    
    try:
        # Remove 'D:' prefix if present
        date_str = pdf_date_str.replace("D:", "")
        
        # Extract date and time components
        # Format: YYYYMMDDHHmmSSOHH'mm'
        match = re.match(r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})([+-]?)(\d{2})'?(\d{2})'?", date_str)
        if not match:
            return None
        
        year, month, day, hour, minute, second, tz_sign, tz_hour, tz_min = match.groups()
        
        # Create datetime object
        dt = datetime(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second)
        )
        
        # Convert to epoch timestamp
        return int(dt.timestamp())
    except (ValueError, AttributeError):
        return None


def read_pdf_content(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Read and extract content from a validated PDF file
    
    Args:
        file_path: Path to PDF file (should be validated first)
        
    Returns:
        Tuple of (text_content, metadata_dict)
        
    Raises:
        PDFValidationError: If PDF is invalid or can't be read
    """
    if PyPDF2 is None:
        raise PDFValidationError("PyPDF2 is not installed. Install it with: pip install PyPDF2")
    
    # Validate first
    is_valid, error_msg = validate_pdf_file(file_path)
    if not is_valid:
        raise PDFValidationError(error_msg or "PDF validation failed")
    
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            metadata: Dict[str, Any] = {}
            if pdf_reader.metadata:
                pdf_metadata = pdf_reader.metadata
                
                # Parse dates to epoch timestamps
                creation_date_str = str(pdf_metadata.get("/CreationDate", ""))
                mod_date_str = str(pdf_metadata.get("/ModDate", ""))
                
                creation_epoch = _parse_pdf_date(creation_date_str)
                mod_epoch = _parse_pdf_date(mod_date_str)
                
                metadata = {
                    "title": str(pdf_metadata.get("/Title", "")),
                    "author": str(pdf_metadata.get("/Author", "")),
                    "subject": str(pdf_metadata.get("/Subject", "")),
                    "creator": str(pdf_metadata.get("/Creator", "")),
                    "producer": str(pdf_metadata.get("/Producer", "")),
                }
                
                # Only add dates if they were successfully parsed
                if creation_epoch is not None:
                    metadata["creation_date_epoch"] = creation_epoch
                if mod_epoch is not None:
                    metadata["modification_date_epoch"] = mod_epoch
            
            # Extract text from all pages
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    text_content += f"\n\n--- Page {page_num} ---\n\n"
                    text_content += page_text
                except Exception as e:
                    # If a page fails, continue with others but note it
                    text_content += f"\n\n--- Page {page_num} ---\n\n[Error extracting text from this page: {str(e)}]"
            
            # Add PDF info to metadata
            metadata.update({
                "source": "pdf",
                "source_file": os.path.basename(file_path),
                "source_path": file_path,
                "total_pages": len(pdf_reader.pages),
                "file_size": os.path.getsize(file_path),
            })
            
            return text_content.strip(), metadata
            
    except PDFValidationError:
        raise
    except Exception as e:
        raise PDFValidationError(f"Error reading PDF content: {str(e)}") from e


def check_pdf_requirements() -> bool:
    """
    Check if PyPDF2 is available
    
    Returns:
        True if PyPDF2 is installed, False otherwise
    """
    return PyPDF2 is not None
