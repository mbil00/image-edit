"""Tests for utility functions."""

import pytest

from image_edit.utils.image import (
    detect_format,
    format_from_extension,
    ImageFormat,
)


class TestDetectFormat:
    """Tests for format detection from magic bytes."""

    def test_detect_png(self):
        # PNG magic bytes
        data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        assert detect_format(data) == ImageFormat.PNG

    def test_detect_jpeg(self):
        # JPEG magic bytes
        data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        assert detect_format(data) == ImageFormat.JPEG

    def test_detect_gif87a(self):
        data = b"GIF87a" + b"\x00" * 100
        assert detect_format(data) == ImageFormat.GIF

    def test_detect_gif89a(self):
        data = b"GIF89a" + b"\x00" * 100
        assert detect_format(data) == ImageFormat.GIF

    def test_detect_webp(self):
        # WebP has RIFF header + WEBP
        data = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
        assert detect_format(data) == ImageFormat.WEBP

    def test_detect_unknown(self):
        data = b"\x00\x00\x00\x00" * 100
        assert detect_format(data) is None

    def test_detect_too_short(self):
        data = b"\x89PN"
        assert detect_format(data) is None


class TestFormatFromExtension:
    """Tests for format detection from file extension."""

    def test_png(self):
        assert format_from_extension("png") == ImageFormat.PNG
        assert format_from_extension(".png") == ImageFormat.PNG
        assert format_from_extension("PNG") == ImageFormat.PNG

    def test_jpeg(self):
        assert format_from_extension("jpg") == ImageFormat.JPEG
        assert format_from_extension("jpeg") == ImageFormat.JPEG
        assert format_from_extension(".jpg") == ImageFormat.JPEG

    def test_webp(self):
        assert format_from_extension("webp") == ImageFormat.WEBP

    def test_gif(self):
        assert format_from_extension("gif") == ImageFormat.GIF

    def test_unknown(self):
        assert format_from_extension("bmp") is None
        assert format_from_extension("tiff") is None


class TestImageFormat:
    """Tests for ImageFormat enum."""

    def test_mime_types(self):
        assert ImageFormat.PNG.mime_type == "image/png"
        assert ImageFormat.JPEG.mime_type == "image/jpeg"
        assert ImageFormat.WEBP.mime_type == "image/webp"
        assert ImageFormat.GIF.mime_type == "image/gif"

    def test_extensions(self):
        assert ImageFormat.PNG.extension == ".png"
        assert ImageFormat.JPEG.extension == ".jpg"
        assert ImageFormat.WEBP.extension == ".webp"
        assert ImageFormat.GIF.extension == ".gif"
