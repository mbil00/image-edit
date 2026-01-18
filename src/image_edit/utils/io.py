"""Binary I/O helpers for stdin/stdout handling."""

import sys
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

import click
from PIL import Image

from .image import detect_format, format_from_extension, ImageFormat


def read_multiple_images(
    input_paths: list[Path],
    allow_stdin_fallback: bool = True,
) -> list[tuple[bytes, Optional[ImageFormat]]]:
    """
    Read multiple image files.

    If only one path provided and stdin has data, uses stdin as second image.

    Args:
        input_paths: List of paths to input files
        allow_stdin_fallback: If True and only one path, try to read stdin as second image

    Returns:
        List of (image bytes, detected format) tuples

    Raises:
        click.ClickException: If input cannot be read or is empty
    """
    images: list[tuple[bytes, Optional[ImageFormat]]] = []

    # Read all specified input files
    for path in input_paths:
        if not path.exists():
            raise click.ClickException(f"Input file not found: {path}")

        data = path.read_bytes()
        if not data:
            raise click.ClickException(f"Input file is empty: {path}")

        # Try to detect format from content first, then extension
        fmt = detect_format(data)
        if fmt is None:
            fmt = format_from_extension(path.suffix)

        images.append((data, fmt))

    # If only one path and stdin has data, use stdin as additional image
    if len(input_paths) == 1 and allow_stdin_fallback and not sys.stdin.isatty():
        stdin = click.get_binary_stream("stdin")
        stdin_data = stdin.read()
        if stdin_data:
            stdin_fmt = detect_format(stdin_data)
            images.insert(0, (stdin_data, stdin_fmt))  # stdin image first

    return images


def read_image_input(
    input_path: Optional[Path] = None,
) -> tuple[bytes, Optional[ImageFormat]]:
    """
    Read image data from file or stdin.

    Args:
        input_path: Path to input file, or None to read from stdin

    Returns:
        Tuple of (image bytes, detected format)

    Raises:
        click.ClickException: If input cannot be read or is empty
    """
    if input_path is not None:
        # Read from file
        if not input_path.exists():
            raise click.ClickException(f"Input file not found: {input_path}")

        data = input_path.read_bytes()
        if not data:
            raise click.ClickException(f"Input file is empty: {input_path}")

        # Try to detect format from content first, then extension
        fmt = detect_format(data)
        if fmt is None:
            fmt = format_from_extension(input_path.suffix)

        return data, fmt

    # Read from stdin
    stdin = click.get_binary_stream("stdin")

    # Check if stdin is a TTY (no piped input)
    if sys.stdin.isatty():
        raise click.ClickException(
            "No input provided. Use -i/--input for a file or pipe an image via stdin."
        )

    data = stdin.read()
    if not data:
        raise click.ClickException("No data received from stdin.")

    fmt = detect_format(data)
    return data, fmt


def write_image_output(
    image_data: bytes,
    output_path: Optional[Path] = None,
    output_format: Optional[ImageFormat] = None,
) -> None:
    """
    Write image data to file or stdout.

    Args:
        image_data: Raw image bytes to write
        output_path: Path to output file, or None to write to stdout
        output_format: Desired output format (for conversion if needed)
    """
    if output_path is not None:
        # Determine output format from path extension if not specified
        if output_format is None:
            output_format = format_from_extension(output_path.suffix)

        # Convert format if needed
        final_data = _convert_format(image_data, output_format)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(final_data)
    else:
        # Write to stdout - convert to PNG by default for consistency
        if output_format is None:
            output_format = ImageFormat.PNG

        final_data = _convert_format(image_data, output_format)

        stdout = click.get_binary_stream("stdout")
        stdout.write(final_data)


def _convert_format(
    image_data: bytes,
    target_format: Optional[ImageFormat],
) -> bytes:
    """
    Convert image data to target format if needed.

    Args:
        image_data: Source image bytes
        target_format: Desired output format

    Returns:
        Image bytes in target format
    """
    if target_format is None:
        return image_data

    source_format = detect_format(image_data)

    # If already in target format, no conversion needed
    if source_format == target_format:
        return image_data

    # Use PIL to convert
    img = Image.open(BytesIO(image_data))

    # Handle RGBA to RGB conversion for JPEG
    if target_format == ImageFormat.JPEG and img.mode == "RGBA":
        # Create white background
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        img = background

    output = BytesIO()
    pil_format = target_format.value.upper()
    if pil_format == "JPEG":
        img.save(output, format=pil_format, quality=95)
    else:
        img.save(output, format=pil_format)

    return output.getvalue()
