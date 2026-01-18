"""Template registry for managing editing templates."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from ..config import get_config_dir


@dataclass
class Template:
    """A predefined image editing template."""

    name: str
    prompt: str
    description: str = ""
    aliases: list[str] = field(default_factory=list)

    @property
    def all_names(self) -> list[str]:
        """Return all names (primary + aliases) for this template."""
        return [self.name] + self.aliases


class TemplateRegistry:
    """Registry for managing and looking up templates."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._templates: dict[str, Template] = {}
        self._alias_map: dict[str, str] = {}

    def register(self, template: Template) -> None:
        """
        Register a template.

        Args:
            template: The template to register
        """
        self._templates[template.name] = template
        for alias in template.aliases:
            self._alias_map[alias] = template.name

    def get(self, name: str) -> Optional[Template]:
        """
        Get a template by name or alias.

        Args:
            name: Template name or alias

        Returns:
            The template if found, None otherwise
        """
        # Check direct name first
        if name in self._templates:
            return self._templates[name]

        # Check aliases
        if name in self._alias_map:
            return self._templates[self._alias_map[name]]

        return None

    def list_all(self) -> list[Template]:
        """Return all registered templates."""
        return list(self._templates.values())

    def load_user_templates(self) -> None:
        """Load user-defined templates from config directory."""
        config_dir = get_config_dir()
        templates_file = config_dir / "templates.toml"

        if not templates_file.exists():
            return

        try:
            with open(templates_file, "rb") as f:
                data = tomllib.load(f)

            for tmpl_data in data.get("template", []):
                template = Template(
                    name=tmpl_data["name"],
                    prompt=tmpl_data["prompt"],
                    description=tmpl_data.get("description", ""),
                    aliases=tmpl_data.get("aliases", []),
                )
                self.register(template)
        except Exception:
            # Silently ignore malformed user templates
            pass


# Global registry instance
_registry: Optional[TemplateRegistry] = None


def get_registry() -> TemplateRegistry:
    """Get the global template registry, initializing if needed."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()

        # Register built-in templates
        from .builtin import BUILTIN_TEMPLATES

        for template in BUILTIN_TEMPLATES:
            _registry.register(template)

        # Load user templates (these can override built-ins)
        _registry.load_user_templates()

    return _registry
