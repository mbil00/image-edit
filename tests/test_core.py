"""Tests for core orchestration logic."""

import pytest

from image_edit.core import resolve_prompt, get_provider


class TestResolvePrompt:
    """Tests for prompt resolution."""

    def test_resolve_template_by_name(self):
        result = resolve_prompt("remove-bg")
        assert "background" in result.lower()
        assert "transparent" in result.lower()

    def test_resolve_template_by_alias(self):
        result = resolve_prompt("nobg")
        assert "background" in result.lower()

    def test_literal_prompt_passthrough(self):
        prompt = "make the image blue and sparkly"
        result = resolve_prompt(prompt)
        assert result == prompt

    def test_unknown_template_treated_as_literal(self):
        prompt = "not-a-real-template"
        result = resolve_prompt(prompt)
        assert result == prompt


class TestGetProvider:
    """Tests for provider lookup."""

    def test_get_gemini_provider(self):
        provider = get_provider("gemini")
        assert provider.name == "gemini"

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown")
