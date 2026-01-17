"""
Filesystem plugin for CMS
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.cms.plugins.base import BasePlugin
from app.services.cms.plugins.utils.filesystem.pdf_utils import (
    PDFValidationError,
    check_pdf_requirements,
    read_pdf_content,
    validate_pdf_file,
)


class FilesystemPlugin(BasePlugin):
    """Plugin for filesystem-based content storage"""

    # pylint: disable=broad-exception-caught

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.base_path = Path(config.get("base_path", "./data/cms") if config else "./data/cms")
        self.connected = False

    async def connect(self) -> bool:
        """Connect to the filesystem (ensure directory exists)"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.connected = True
        return True

    async def disconnect(self) -> bool:
        """Disconnect from the filesystem"""
        self.connected = False
        return True

    def _get_file_path(self, content_id: str) -> Path:
        """Get file path for a content ID"""
        return self.base_path / f"{content_id}.json"

    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from filesystem"""
        if not self.connected:
            await self.connect()

        file_path = self._get_file_path(content_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)  # type: ignore[no-any-return]
        except Exception:
            return None

    async def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new content in filesystem"""
        if not self.connected:
            await self.connect()

        # Handle PDF file_path if provided
        body = content_data.get("body", "")
        # Get request metadata (user-provided)
        request_metadata = content_data.get("metadata", {}).copy() if content_data.get("metadata") else {}
        
        file_path = content_data.get("file_path")
        if file_path:
            # Validate and process PDF
            if not check_pdf_requirements():
                raise ValueError("PyPDF2 is required for PDF processing. Install it with: pip install PyPDF2")
            
            is_valid, error_msg = validate_pdf_file(file_path)
            if not is_valid:
                raise ValueError(f"PDF validation failed: {error_msg}")
            
            # Read PDF content
            try:
                pdf_text, pdf_metadata = read_pdf_content(file_path)
                # Use PDF text as body if body not provided
                if not body:
                    body = pdf_text
                # Merge metadata: PDF metadata first (base), then request metadata on top (takes precedence)
                metadata = {**pdf_metadata, **request_metadata}
            except PDFValidationError as e:
                raise ValueError(f"Error processing PDF: {str(e)}") from e
        else:
            # No PDF, just use request metadata
            metadata = request_metadata

        if not body:
            raise ValueError("Either 'body' or 'file_path' must be provided")

        content_id = content_data.get("id") or f"fs_{len(list(self.base_path.glob('*.json'))) + 1}"
        content = {
            "id": content_id,
            "title": content_data.get("title", ""),
            "body": body,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "plugin": "filesystem",
        }

        file_path = self._get_file_path(content_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)

        return content

    async def update_content(self, content_id: str, content_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing content in filesystem"""
        if not self.connected:
            await self.connect()

        file_path = self._get_file_path(content_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)

            existing.update(
                {
                    "title": content_data.get("title", existing.get("title")),
                    "body": content_data.get("body", existing.get("body")),
                    "metadata": {**existing.get("metadata", {}), **content_data.get("metadata", {})},
                    "updated_at": datetime.utcnow().isoformat(),
                }
            )

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)

            return existing  # type: ignore[no-any-return]
        except Exception:
            return None

    async def delete_content(self, content_id: str) -> bool:
        """Delete content from filesystem"""
        if not self.connected:
            await self.connect()

        file_path = self._get_file_path(content_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def list_content(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all content from filesystem with pagination"""
        if not self.connected:
            await self.connect()

        results = []
        json_files = sorted(self.base_path.glob("*.json"))[offset : offset + limit]

        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    results.append(json.load(f))
            except Exception:
                continue

        return results

    async def search_content(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search content in filesystem"""
        if not self.connected:
            await self.connect()

        results = []
        query_lower = query.lower()

        for file_path in self.base_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if (
                        query_lower in content.get("title", "").lower()
                        or query_lower in content.get("body", "").lower()
                    ):
                        results.append(content)
                    if len(results) >= limit:
                        break
            except Exception:
                continue

        return results
