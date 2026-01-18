"""Image format detection and handling utilities."""

from enum import Enum
from typing import Optional


class ImageFormat(str, Enum):
    """Supported image formats."""

    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    GIF = "gif"

    @property
    def mime_type(self) -> str:
        """Get the MIME type for this format."""
        return f"image/{self.value}"

    @property
    def extension(self) -> str:
        """Get the file extension for this format."""
        if self == ImageFormat.JPEG:
            return ".jpg"
        return f".{self.value}"


# Magic bytes for image format detection
MAGIC_BYTES = {
    b"\x89PNG\r\n\x1a\n": ImageFormat.PNG,
    b"\xff\xd8\xff": ImageFormat.JPEG,
    b"RIFF": ImageFormat.WEBP,  # WebP starts with RIFF
    b"GIF87a": ImageFormat.GIF,
    b"GIF89a": ImageFormat.GIF,
}


def detect_format(data: bytes) -> Optional[ImageFormat]:
    """
    Detect image format from binary data using magic bytes.

    Args:
        data: Raw image bytes (at least first 12 bytes needed)

    Returns:
        Detected ImageFormat or None if unknown
    """
    if len(data) < 4:
        return None

    # Check PNG (8 bytes)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ImageFormat.PNG

    # Check JPEG (3 bytes)
    if data[:3] == b"\xff\xd8\xff":
        return ImageFormat.JPEG

    # Check WebP (requires checking RIFF header + WEBP)
    if data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"WEBP":
        return ImageFormat.WEBP

    # Check GIF (6 bytes)
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ImageFormat.GIF

    return None


def format_from_extension(ext: str) -> Optional[ImageFormat]:
    """
    Get image format from file extension.

    Args:
        ext: File extension (with or without leading dot)

    Returns:
        ImageFormat or None if unknown
    """
    ext = ext.lower().lstrip(".")

    mapping = {
        "png": ImageFormat.PNG,
        "jpg": ImageFormat.JPEG,
        "jpeg": ImageFormat.JPEG,
        "webp": ImageFormat.WEBP,
        "gif": ImageFormat.GIF,
    }

    return mapping.get(ext)
