"""CLI interface for image-edit."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import (
    get_settings,
    get_config_value,
    set_config_value,
    unset_config_value,
    get_all_config,
    get_config_file,
    CONFIG_KEYS,
    DEFAULTS,
)
from .core import run_edit, run_generate, get_provider
from .providers import ProviderError
from .templates import get_registry
from .utils import read_image_input, write_image_output
from .utils.image import format_from_extension, ImageFormat

app = typer.Typer(
    name="image-edit",
    help="AI-powered image editing CLI with Unix piping support.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console(stderr=True)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"image-edit version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """AI-powered image editing CLI with Unix piping support."""
    pass


@app.command()
def edit(
    prompt: Annotated[
        str,
        typer.Argument(
            help="Edit instruction or template name (e.g., 'make it blue' or 'remove-bg')"
        ),
    ],
    input_file: Annotated[
        Optional[Path],
        typer.Option(
            "--input",
            "-i",
            help="Input image file. If not provided, reads from stdin.",
        ),
    ] = None,
    output_file: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output image file. If not provided, writes to stdout.",
        ),
    ] = None,
    output_format: Annotated[
        Optional[str],
        typer.Option(
            "--format",
            "-f",
            help="Output format: png, jpeg, webp, gif",
        ),
    ] = None,
    provider: Annotated[
        str,
        typer.Option(
            "--provider",
            "-p",
            help="AI provider to use.",
        ),
    ] = "gemini",
) -> None:
    """
    Edit an image using AI.

    Examples:
        image-edit "make the sky purple" -i sunset.jpg -o result.png
        cat photo.png | image-edit "watercolor style" > art.png
        image-edit remove-bg -i portrait.jpg -o nobg.png
    """
    try:
        # Read input
        with console.status("[bold blue]Reading image..."):
            image_data, detected_format = read_image_input(input_file)

        mime_type = detected_format.mime_type if detected_format else None

        # Parse output format
        fmt: Optional[ImageFormat] = None
        if output_format:
            fmt = format_from_extension(output_format)
            if fmt is None:
                console.print(f"[red]Unknown format: {output_format}[/red]")
                raise typer.Exit(1)

        # Perform edit
        with console.status(f"[bold blue]Editing with {provider}..."):
            result = run_edit(image_data, prompt, provider, mime_type)

        # Write output
        write_image_output(result.image_data, output_file, fmt)

        if output_file:
            console.print(f"[green]Saved to {output_file}[/green]")

    except ProviderError as e:
        console.print(f"[red]Provider error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def generate(
    prompt: Annotated[
        str,
        typer.Argument(help="Description of the image to generate"),
    ],
    output_file: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output image file. If not provided, writes to stdout.",
        ),
    ] = None,
    output_format: Annotated[
        Optional[str],
        typer.Option(
            "--format",
            "-f",
            help="Output format: png, jpeg, webp, gif",
        ),
    ] = None,
    provider: Annotated[
        str,
        typer.Option(
            "--provider",
            "-p",
            help="AI provider to use.",
        ),
    ] = "gemini",
) -> None:
    """
    Generate a new image from a text description.

    Examples:
        image-edit generate "a sunset over mountains" -o sunset.png
        image-edit generate "abstract art" > art.png
    """
    try:
        # Parse output format
        fmt: Optional[ImageFormat] = None
        if output_format:
            fmt = format_from_extension(output_format)
            if fmt is None:
                console.print(f"[red]Unknown format: {output_format}[/red]")
                raise typer.Exit(1)

        # Generate image
        with console.status(f"[bold blue]Generating with {provider}..."):
            result = run_generate(prompt, provider)

        # Write output
        write_image_output(result.image_data, output_file, fmt)

        if output_file:
            console.print(f"[green]Saved to {output_file}[/green]")

    except ProviderError as e:
        console.print(f"[red]Provider error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def templates() -> None:
    """List available editing templates."""
    registry = get_registry()
    all_templates = registry.list_all()

    table = Table(title="Available Templates")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Aliases", style="dim")
    table.add_column("Description", style="green")

    for tmpl in sorted(all_templates, key=lambda t: t.name):
        aliases = ", ".join(tmpl.aliases) if tmpl.aliases else "-"
        table.add_row(tmpl.name, aliases, tmpl.description)

    console.print(table)


@app.command()
def providers() -> None:
    """Show available providers and their status."""
    settings = get_settings()

    table = Table(title="Providers")
    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Model", style="dim")
    table.add_column("Status", style="bold")

    # Check Gemini
    gemini = get_provider("gemini")
    gemini_status = (
        "[green]Configured[/green]"
        if gemini.is_configured
        else "[red]API key missing[/red]"
    )
    table.add_row("gemini", settings.gemini_model, gemini_status)

    console.print(table)

    if not gemini.is_configured:
        console.print()
        console.print("[yellow]To configure Gemini:[/yellow]")
        console.print("  image-edit config set api-key YOUR_API_KEY")


# Config subcommand group
config_app = typer.Typer(
    name="config",
    help="Manage configuration settings.",
    no_args_is_help=True,
)
app.add_typer(config_app, name="config")


@config_app.command("set")
def config_set(
    key: Annotated[
        str,
        typer.Argument(help="Configuration key (e.g., api-key, model)"),
    ],
    value: Annotated[
        str,
        typer.Argument(help="Value to set"),
    ],
) -> None:
    """
    Set a configuration value.

    Examples:
        image-edit config set api-key YOUR_API_KEY
        image-edit config set model gemini-2.5-flash-preview-05-20
    """
    try:
        set_config_value(key, value)
        # Mask API key in output
        display_value = "****" + value[-4:] if key == "api-key" and len(value) > 4 else value
        console.print(f"[green]Set {key} = {display_value}[/green]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@config_app.command("get")
def config_get(
    key: Annotated[
        str,
        typer.Argument(help="Configuration key to get"),
    ],
) -> None:
    """
    Get a configuration value.

    Examples:
        image-edit config get model
        image-edit config get api-key
    """
    if key not in CONFIG_KEYS:
        valid_keys = ", ".join(CONFIG_KEYS.keys())
        console.print(f"[red]Unknown key '{key}'. Valid keys: {valid_keys}[/red]")
        raise typer.Exit(1)

    value = get_config_value(key)
    if value is None:
        console.print(f"[dim]{key}: (not set)[/dim]")
    elif key == "api-key":
        # Mask API key
        masked = "****" + value[-4:] if len(value) > 4 else "****"
        console.print(f"{key}: {masked}")
    else:
        console.print(f"{key}: {value}")


@config_app.command("unset")
def config_unset(
    key: Annotated[
        str,
        typer.Argument(help="Configuration key to remove"),
    ],
) -> None:
    """
    Remove a configuration value from the config file.

    Examples:
        image-edit config unset model
    """
    if unset_config_value(key):
        console.print(f"[green]Removed {key} from config[/green]")
    else:
        console.print(f"[dim]{key} was not set in config file[/dim]")


@config_app.command("show")
def config_show() -> None:
    """
    Show all configuration values.

    Displays effective values from config file, environment, and defaults.
    """
    table = Table(title="Configuration")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Description", style="dim")

    all_config = get_all_config()

    for key, value in all_config.items():
        description = CONFIG_KEYS.get(key, "")
        if value is None:
            display_value = "[dim](not set)[/dim]"
        elif key == "api-key":
            # Mask API key
            display_value = "****" + value[-4:] if len(value) > 4 else "****"
        else:
            display_value = value
            # Indicate if it's a default
            if key in DEFAULTS and value == DEFAULTS[key]:
                display_value = f"{value} [dim](default)[/dim]"

        table.add_row(key, display_value, description)

    console.print(table)
    console.print()
    console.print(f"[dim]Config file: {get_config_file()}[/dim]")


if __name__ == "__main__":
    app()
