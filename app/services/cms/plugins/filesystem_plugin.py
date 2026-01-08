"""
Filesystem plugin for CMS
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.services.cms.plugins.base import BasePlugin


class FilesystemPlugin(BasePlugin):
    """Plugin for filesystem-based content storage"""
    
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
                return json.load(f)
        except Exception:
            return None
    
    async def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new content in filesystem"""
        if not self.connected:
            await self.connect()
        
        content_id = content_data.get("id") or f"fs_{len(list(self.base_path.glob('*.json'))) + 1}"
        content = {
            "id": content_id,
            "title": content_data.get("title", ""),
            "body": content_data.get("body", ""),
            "metadata": content_data.get("metadata", {}),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "plugin": "filesystem"
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
            
            existing.update({
                "title": content_data.get("title", existing.get("title")),
                "body": content_data.get("body", existing.get("body")),
                "metadata": {**existing.get("metadata", {}), **content_data.get("metadata", {})},
                "updated_at": datetime.utcnow().isoformat()
            })
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
            
            return existing
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
        json_files = sorted(self.base_path.glob("*.json"))[offset:offset + limit]
        
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
                    if (query_lower in content.get("title", "").lower() or 
                        query_lower in content.get("body", "").lower()):
                        results.append(content)
                    if len(results) >= limit:
                        break
            except Exception:
                continue
        
        return results

