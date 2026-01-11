"""
Content Management System service
"""
from typing import Any, Dict, List, Optional

from app.services.cms.plugins.registry import PluginRegistry


class CMSService:
    """Service for content management operations"""

    def __init__(self):
        self.plugin_registry = PluginRegistry()

    async def get_content(self, content_id: str, plugin_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        plugin = self.plugin_registry.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        return await plugin.get_content(content_id)

    async def create_content(self, content_data: Dict[str, Any], plugin_name: Optional[str] = None) -> Dict[str, Any]:
        """Create new content"""
        plugin = self.plugin_registry.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        return await plugin.create_content(content_data)

    async def update_content(
        self, content_id: str, content_data: Dict[str, Any], plugin_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update existing content"""
        plugin = self.plugin_registry.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        return await plugin.update_content(content_id, content_data)

    async def delete_content(self, content_id: str, plugin_name: Optional[str] = None) -> bool:
        """Delete content"""
        plugin = self.plugin_registry.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        return await plugin.delete_content(content_id)

    async def list_content(
        self, plugin_name: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all content"""
        plugin = self.plugin_registry.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        return await plugin.list_content(limit=limit, offset=offset)

    def get_available_plugins(self) -> List[str]:
        """Get list of available plugins"""
        return self.plugin_registry.list_plugins()
