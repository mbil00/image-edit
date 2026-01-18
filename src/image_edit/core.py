"""Core orchestration logic for image editing operations."""

import asyncio
from typing import Optional

from .providers import GeminiProvider, Provider, ProviderError
from .providers.base import EditResult
from .templates import get_registry


def get_provider(name: str = "gemini") -> Provider:
    """
    Get a provider instance by name.

    Args:
        name: Provider name (currently only "gemini" supported)

    Returns:
        Provider instance

    Raises:
        ValueError: If provider name is unknown
    """
    providers = {
        "gemini": GeminiProvider,
    }

    if name not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")

    return providers[name]()


def resolve_prompt(prompt_or_template: str) -> str:
    """
    Resolve a prompt, expanding template names if found.

    Args:
        prompt_or_template: Either a template name/alias or a literal prompt

    Returns:
        The resolved prompt text
    """
    registry = get_registry()
    template = registry.get(prompt_or_template)

    if template is not None:
        return template.prompt

    return prompt_or_template


async def edit_image(
    image_data: bytes,
    prompt: str,
    provider_name: str = "gemini",
    mime_type: Optional[str] = None,
) -> EditResult:
    """
    Edit an image using the specified provider.

    Args:
        image_data: Raw image bytes
        prompt: Edit instruction (can be a template name or literal prompt)
        provider_name: Name of the provider to use
        mime_type: MIME type of the input image

    Returns:
        EditResult with the edited image

    Raises:
        ProviderError: If editing fails
    """
    provider = get_provider(provider_name)
    resolved_prompt = resolve_prompt(prompt)

    return await provider.edit(image_data, resolved_prompt, mime_type)


async def generate_image(
    prompt: str,
    provider_name: str = "gemini",
) -> EditResult:
    """
    Generate a new image from a text prompt.

    Args:
        prompt: Text description of the image to generate
        provider_name: Name of the provider to use

    Returns:
        EditResult with the generated image

    Raises:
        ProviderError: If generation fails
    """
    provider = get_provider(provider_name)
    return await provider.generate(prompt)


def run_edit(
    image_data: bytes,
    prompt: str,
    provider_name: str = "gemini",
    mime_type: Optional[str] = None,
) -> EditResult:
    """
    Synchronous wrapper for edit_image.

    Args:
        image_data: Raw image bytes
        prompt: Edit instruction
        provider_name: Name of the provider to use
        mime_type: MIME type of the input image

    Returns:
        EditResult with the edited image
    """
    return asyncio.run(edit_image(image_data, prompt, provider_name, mime_type))


def run_generate(
    prompt: str,
    provider_name: str = "gemini",
) -> EditResult:
    """
    Synchronous wrapper for generate_image.

    Args:
        prompt: Text description of the image to generate
        provider_name: Name of the provider to use

    Returns:
        EditResult with the generated image
    """
    return asyncio.run(generate_image(prompt, provider_name))


async def combine_images(
    images: list[tuple[bytes, Optional[str]]],
    prompt: str,
    provider_name: str = "gemini",
) -> EditResult:
    """
    Combine multiple images using the specified provider.

    Args:
        images: List of (image_data, mime_type) tuples
        prompt: Text description of how to combine the images
        provider_name: Name of the provider to use

    Returns:
        EditResult with the combined image

    Raises:
        ValueError: If fewer than 2 images provided
        ProviderError: If combining fails
    """
    if len(images) < 2:
        raise ValueError("At least 2 images are required for combine operation")
    provider = get_provider(provider_name)
    return await provider.combine(images, prompt)


def run_combine(
    images: list[tuple[bytes, Optional[str]]],
    prompt: str,
    provider_name: str = "gemini",
) -> EditResult:
    """
    Synchronous wrapper for combine_images.

    Args:
        images: List of (image_data, mime_type) tuples
        prompt: Text description of how to combine the images
        provider_name: Name of the provider to use

    Returns:
        EditResult with the combined image
    """
    return asyncio.run(combine_images(images, prompt, provider_name))
