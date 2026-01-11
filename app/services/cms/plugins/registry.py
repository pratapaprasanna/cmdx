"""
Plugin registry for managing CMS plugins
"""
from typing import Dict, Optional

from app.services.cms.plugins.base import BasePlugin
from app.services.cms.plugins.database_plugin import DatabasePlugin
from app.services.cms.plugins.filesystem_plugin import FilesystemPlugin


class PluginRegistry:
    """Registry for managing and accessing CMS plugins"""

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._default_plugin: Optional[str] = None
        self._initialize_default_plugins()

    def _initialize_default_plugins(self):
        """Initialize default plugins"""
        # Register database plugin (PostgreSQL) as default
        db_plugin = DatabasePlugin("database", {})
        self.register_plugin(db_plugin)
        self._default_plugin = "database"

        # Register filesystem plugin
        fs_plugin = FilesystemPlugin("filesystem", {"base_path": "./data/cms"})
        self.register_plugin(fs_plugin)

    def register_plugin(self, plugin: BasePlugin):
        """Register a new plugin"""
        self._plugins[plugin.name] = plugin

    def get_plugin(self, plugin_name: Optional[str] = None) -> Optional[BasePlugin]:
        """Get a plugin by name, or return default plugin"""
        if plugin_name is None:
            plugin_name = self._default_plugin

        return self._plugins.get(plugin_name)

    def list_plugins(self) -> list:
        """List all registered plugin names"""
        return list(self._plugins.keys())

    def set_default_plugin(self, plugin_name: str):
        """Set the default plugin"""
        if plugin_name not in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        self._default_plugin = plugin_name
