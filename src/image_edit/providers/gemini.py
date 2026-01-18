"""Gemini provider for image editing using Google's Gemini API."""

import base64
from typing import Optional

from google import genai
from google.genai import types

from ..config import get_settings
from ..utils.image import detect_format, ImageFormat
from .base import Provider, ProviderError, EditResult


class GeminiProvider(Provider):
    """Image editing provider using Google's Gemini API."""

    def __init__(self) -> None:
        """Initialize the Gemini provider."""
        self._client: Optional[genai.Client] = None

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "gemini"

    @property
    def model_name(self) -> str:
        """Get the configured model name."""
        return get_settings().gemini_model

    @property
    def is_configured(self) -> bool:
        """Check if Gemini API key is configured."""
        return get_settings().has_gemini_key

    def _get_client(self) -> genai.Client:
        """Get or create the Gemini client."""
        if self._client is None:
            settings = get_settings()
            if not settings.gemini_api_key:
                raise ProviderError(
                    "Gemini API key not configured. "
                    "Run 'image-edit config set api-key YOUR_KEY' or set GEMINI_API_KEY."
                )
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    async def edit(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: Optional[str] = None,
    ) -> EditResult:
        """
        Edit an image using Gemini.

        Args:
            image_data: Raw image bytes
            prompt: Text description of the desired edit
            mime_type: MIME type of the input image

        Returns:
            EditResult containing the edited image
        """
        client = self._get_client()

        # Detect format if not provided
        if mime_type is None:
            fmt = detect_format(image_data)
            mime_type = fmt.mime_type if fmt else "image/png"

        # Encode image as base64
        image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_bytes(
                                data=image_data,
                                mime_type=mime_type,
                            ),
                            types.Part.from_text(text=prompt),
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            # Extract image from response
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return EditResult(
                        image_data=part.inline_data.data,
                        mime_type=part.inline_data.mime_type,
                        provider=self.name,
                        model=self.model_name,
                    )

            # No image in response - check for text error
            text_parts = [
                p.text for p in response.candidates[0].content.parts if p.text
            ]
            if text_parts:
                raise ProviderError(
                    f"Gemini returned text instead of image: {' '.join(text_parts)}"
                )

            raise ProviderError("Gemini response contained no image data")

        except Exception as e:
            if isinstance(e, ProviderError):
                raise
            raise ProviderError(f"Gemini API error: {e}") from e

    async def generate(
        self,
        prompt: str,
    ) -> EditResult:
        """
        Generate a new image from text using Gemini.

        Args:
            prompt: Text description of the image to generate

        Returns:
            EditResult containing the generated image
        """
        client = self._get_client()

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            # Extract image from response
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return EditResult(
                        image_data=part.inline_data.data,
                        mime_type=part.inline_data.mime_type,
                        provider=self.name,
                        model=self.model_name,
                    )

            raise ProviderError("Gemini response contained no image data")

        except Exception as e:
            if isinstance(e, ProviderError):
                raise
            raise ProviderError(f"Gemini API error: {e}") from e

    async def combine(
        self,
        images: list[tuple[bytes, Optional[str]]],
        prompt: str,
    ) -> EditResult:
        """
        Combine multiple images using Gemini.

        Args:
            images: List of (image_data, mime_type) tuples
            prompt: Text description of how to combine the images

        Returns:
            EditResult containing the combined image
        """
        client = self._get_client()

        # Build parts list with all images followed by prompt
        parts = []
        for image_data, mime_type in images:
            if mime_type is None:
                fmt = detect_format(image_data)
                mime_type = fmt.mime_type if fmt else "image/png"
            parts.append(types.Part.from_bytes(data=image_data, mime_type=mime_type))

        parts.append(types.Part.from_text(text=prompt))

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(parts=parts)],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            # Extract image from response
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return EditResult(
                        image_data=part.inline_data.data,
                        mime_type=part.inline_data.mime_type,
                        provider=self.name,
                        model=self.model_name,
                    )

            # No image in response - check for text error
            text_parts = [
                p.text for p in response.candidates[0].content.parts if p.text
            ]
            if text_parts:
                raise ProviderError(
                    f"Gemini returned text instead of image: {' '.join(text_parts)}"
                )

            raise ProviderError("Gemini response contained no image data")

        except Exception as e:
            if isinstance(e, ProviderError):
                raise
            raise ProviderError(f"Gemini API error: {e}") from e
