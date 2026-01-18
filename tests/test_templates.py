"""Tests for the template system."""

import pytest

from image_edit.templates import Template, TemplateRegistry, BUILTIN_TEMPLATES


class TestTemplate:
    """Tests for the Template dataclass."""

    def test_all_names_includes_primary_and_aliases(self):
        template = Template(
            name="test",
            prompt="Test prompt",
            aliases=["t", "tst"],
        )
        assert template.all_names == ["test", "t", "tst"]

    def test_all_names_with_no_aliases(self):
        template = Template(
            name="test",
            prompt="Test prompt",
        )
        assert template.all_names == ["test"]


class TestTemplateRegistry:
    """Tests for the TemplateRegistry."""

    def test_register_and_get_by_name(self):
        registry = TemplateRegistry()
        template = Template(name="test", prompt="Test prompt")
        registry.register(template)

        result = registry.get("test")
        assert result is template

    def test_get_by_alias(self):
        registry = TemplateRegistry()
        template = Template(
            name="test",
            prompt="Test prompt",
            aliases=["t", "tst"],
        )
        registry.register(template)

        assert registry.get("t") is template
        assert registry.get("tst") is template

    def test_get_unknown_returns_none(self):
        registry = TemplateRegistry()
        assert registry.get("unknown") is None

    def test_list_all(self):
        registry = TemplateRegistry()
        t1 = Template(name="test1", prompt="Prompt 1")
        t2 = Template(name="test2", prompt="Prompt 2")
        registry.register(t1)
        registry.register(t2)

        all_templates = registry.list_all()
        assert len(all_templates) == 2
        assert t1 in all_templates
        assert t2 in all_templates


class TestBuiltinTemplates:
    """Tests for built-in templates."""

    def test_builtin_templates_exist(self):
        assert len(BUILTIN_TEMPLATES) > 0

    def test_required_templates_present(self):
        names = [t.name for t in BUILTIN_TEMPLATES]
        required = ["remove-bg", "enhance", "upscale", "vintage", "sepia", "sharpen"]
        for name in required:
            assert name in names, f"Required template '{name}' not found"

    def test_all_templates_have_prompts(self):
        for template in BUILTIN_TEMPLATES:
            assert template.prompt, f"Template '{template.name}' has empty prompt"
            assert len(template.prompt) > 10, f"Template '{template.name}' prompt too short"
