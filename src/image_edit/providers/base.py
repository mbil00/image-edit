"""Abstract base class for image editing providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class ProviderError(Exception):
    """Base exception for provider errors."""

    pass


@dataclass
class EditResult:
    """Result from an image edit operation."""

    image_data: bytes
    mime_type: str
    provider: str
    model: Optional[str] = None


class Provider(ABC):
    """Abstract base class for image editing providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured (API key, etc.)."""
        pass

    @abstractmethod
    async def edit(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: Optional[str] = None,
    ) -> EditResult:
        """
        Edit an image using the given prompt.

        Args:
            image_data: Raw image bytes
            prompt: Text description of the desired edit
            mime_type: MIME type of the input image

        Returns:
            EditResult containing the edited image

        Raises:
            ProviderError: If the edit operation fails
        """
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
    ) -> EditResult:
        """
        Generate a new image from a text prompt.

        Args:
            prompt: Text description of the image to generate

        Returns:
            EditResult containing the generated image

        Raises:
            ProviderError: If generation fails
        """
        pass
