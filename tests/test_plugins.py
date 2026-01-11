"""
Tests for CMS plugins
"""
import pytest

from app.services.cms.plugins.database_plugin import DatabasePlugin
from app.services.cms.plugins.filesystem_plugin import FilesystemPlugin
from app.services.cms.plugins.registry import PluginRegistry


@pytest.mark.asyncio
async def test_database_plugin():
    """Test database plugin operations"""
    plugin = DatabasePlugin("test_db", {})

    # Connect
    assert await plugin.connect() is True

    # Create content
    content = await plugin.create_content({"title": "Test Title", "body": "Test Body", "metadata": {"test": "value"}})
    assert content["title"] == "Test Title"
    assert "id" in content

    content_id = content["id"]

    # Get content
    retrieved = await plugin.get_content(content_id)
    assert retrieved is not None
    assert retrieved["title"] == "Test Title"

    # Update content
    updated = await plugin.update_content(content_id, {"title": "Updated Title"})
    assert updated["title"] == "Updated Title"

    # List content
    all_content = await plugin.list_content()
    assert len(all_content) >= 1

    # Search content
    search_results = await plugin.search_content("Test")
    assert len(search_results) >= 1

    # Delete content
    deleted = await plugin.delete_content(content_id)
    assert deleted is True

    # Verify deletion
    retrieved_after = await plugin.get_content(content_id)
    assert retrieved_after is None

    # Disconnect
    assert await plugin.disconnect() is True


@pytest.mark.asyncio
async def test_filesystem_plugin(tmp_path):
    """Test filesystem plugin operations"""
    plugin = FilesystemPlugin("test_fs", {"base_path": str(tmp_path / "cms")})

    # Connect
    assert await plugin.connect() is True

    # Create content
    content = await plugin.create_content(
        {"title": "FS Test Title", "body": "FS Test Body", "metadata": {"test": "value"}}
    )
    assert content["title"] == "FS Test Title"
    assert "id" in content

    content_id = content["id"]

    # Get content
    retrieved = await plugin.get_content(content_id)
    assert retrieved is not None
    assert retrieved["title"] == "FS Test Title"

    # Update content
    updated = await plugin.update_content(content_id, {"title": "FS Updated Title"})
    assert updated["title"] == "FS Updated Title"

    # List content
    all_content = await plugin.list_content()
    assert len(all_content) >= 1

    # Search content
    search_results = await plugin.search_content("FS")
    assert len(search_results) >= 1

    # Delete content
    deleted = await plugin.delete_content(content_id)
    assert deleted is True

    # Verify deletion
    retrieved_after = await plugin.get_content(content_id)
    assert retrieved_after is None

    # Disconnect
    assert await plugin.disconnect() is True


def test_plugin_registry():
    """Test plugin registry"""
    registry = PluginRegistry()

    # Check default plugins are registered
    plugins = registry.list_plugins()
    assert "database" in plugins
    assert "filesystem" in plugins

    # Get default plugin
    default_plugin = registry.get_plugin()
    assert default_plugin is not None
    assert default_plugin.name == "database"

    # Get specific plugin
    fs_plugin = registry.get_plugin("filesystem")
    assert fs_plugin is not None
    assert fs_plugin.name == "filesystem"

    # Set default plugin
    registry.set_default_plugin("filesystem")
    new_default = registry.get_plugin()
    assert new_default.name == "filesystem"
