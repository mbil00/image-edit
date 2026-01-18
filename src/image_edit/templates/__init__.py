"""Template system for predefined editing operations."""

from .registry import Template, TemplateRegistry, get_registry
from .builtin import BUILTIN_TEMPLATES

__all__ = [
    "Template",
    "TemplateRegistry",
    "get_registry",
    "BUILTIN_TEMPLATES",
]
