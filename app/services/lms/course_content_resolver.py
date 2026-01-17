"""
Service for resolving CMS content in LMS courses
"""
from typing import Any, Dict, List, Optional

from app.services.cms.cms_service import CMSService
from app.services.cms.plugins.registry import PluginRegistry


class CourseContentResolver:
    """Resolves CMS content references in course modules"""

    def __init__(self):
        self.cms_service = CMSService()
        self.plugin_registry = PluginRegistry()

    async def resolve_module_content(
        self, module: Dict[str, Any], include_content: bool = True
    ) -> Dict[str, Any]:
        """
        Resolve content items in a module

        Args:
            module: Module dictionary with content_items
            include_content: If True, fetch full content; if False, just validate

        Returns:
            Module with resolved content items
        """
        resolved_module = module.copy()
        content_items = module.get("content_items", [])

        resolved_items = []
        for item in content_items:
            content_id = item.get("content_id")
            plugin_name = item.get("plugin")

            if not content_id or not plugin_name:
                continue

            resolved_item = item.copy()

            if include_content:
                # Fetch content from CMS
                try:
                    content = await self.cms_service.get_content(content_id, plugin_name=plugin_name)
                    if content:
                        resolved_item["content"] = content
                        resolved_item["content_resolved"] = True
                    else:
                        resolved_item["content"] = None
                        resolved_item["content_resolved"] = False
                        resolved_item["error"] = "Content not found"
                except Exception as e:
                    resolved_item["content"] = None
                    resolved_item["content_resolved"] = False
                    resolved_item["error"] = str(e)
            else:
                # Just validate content exists
                try:
                    content = await self.cms_service.get_content(content_id, plugin_name=plugin_name)
                    resolved_item["content_exists"] = content is not None
                except Exception:
                    resolved_item["content_exists"] = False

            resolved_items.append(resolved_item)

        resolved_module["content_items"] = resolved_items
        return resolved_module

    async def resolve_course_modules(
        self, course_data: Dict[str, Any], include_content: bool = True
    ) -> Dict[str, Any]:
        """
        Resolve all content in course modules

        Args:
            course_data: Course data dictionary with modules
            include_content: If True, fetch full content; if False, just validate

        Returns:
            Course data with resolved modules
        """
        resolved_course = course_data.copy()
        modules = course_data.get("modules", [])

        resolved_modules = []
        for module in modules:
            # Handle both old format (plain dict) and new format (with content_items)
            if isinstance(module, dict):
                if "content_items" in module:
                    resolved_module = await self.resolve_module_content(module, include_content)
                else:
                    # Legacy format - no content items
                    resolved_module = module
                resolved_modules.append(resolved_module)

        resolved_course["modules"] = resolved_modules
        return resolved_course

    async def validate_content_references(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that all content references in modules exist

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "missing_content": [],
        }

        for module in modules:
            content_items = module.get("content_items", [])
            for item in content_items:
                content_id = item.get("content_id")
                plugin_name = item.get("plugin")

                if not content_id or not plugin_name:
                    validation_result["errors"].append(
                        {
                            "module_id": module.get("id"),
                            "error": "Missing content_id or plugin",
                        }
                    )
                    validation_result["valid"] = False
                    continue

                try:
                    content = await self.cms_service.get_content(content_id, plugin_name=plugin_name)
                    if not content:
                        validation_result["missing_content"].append(
                            {
                                "module_id": module.get("id"),
                                "content_id": content_id,
                                "plugin": plugin_name,
                            }
                        )
                        validation_result["valid"] = False
                except Exception as e:
                    validation_result["errors"].append(
                        {
                            "module_id": module.get("id"),
                            "content_id": content_id,
                            "plugin": plugin_name,
                            "error": str(e),
                        }
                    )
                    validation_result["valid"] = False

        return validation_result
