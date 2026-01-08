"""
Base plugin interface for CMS plugins
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BasePlugin(ABC):
    """Base class for all CMS plugins"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the data source"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the data source"""
        pass
    
    @abstractmethod
    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        pass
    
    @abstractmethod
    async def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new content"""
        pass
    
    @abstractmethod
    async def update_content(self, content_id: str, content_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing content"""
        pass
    
    @abstractmethod
    async def delete_content(self, content_id: str) -> bool:
        """Delete content"""
        pass
    
    @abstractmethod
    async def list_content(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all content with pagination"""
        pass
    
    @abstractmethod
    async def search_content(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search content"""
        pass

