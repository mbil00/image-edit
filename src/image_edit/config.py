"""Configuration management for image-edit CLI."""

import os
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import tomli_w


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    config_dir = Path.home() / ".config" / "image-edit"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config.toml"


# Valid configuration keys and their descriptions
CONFIG_KEYS = {
    "api-key": "Gemini API key for authentication",
    "model": "Gemini model to use (e.g., gemini-3-pro-image-preview, gemini-2.0-flash-exp)",
    "default-format": "Default output format (png, jpeg, webp, gif)",
    "default-quality": "Default quality setting",
}

# Default values
DEFAULTS = {
    "model": "gemini-3-pro-image-preview",
    "default-format": "png",
    "default-quality": "1K",
}


def _load_config_file() -> dict[str, Any]:
    """Load configuration from the TOML file."""
    config_file = get_config_file()
    if not config_file.exists():
        return {}

    try:
        with open(config_file, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _save_config_file(config: dict[str, Any]) -> None:
    """Save configuration to the TOML file."""
    config_file = get_config_file()
    with open(config_file, "wb") as f:
        tomli_w.dump(config, f)


def get_config_value(key: str) -> Optional[str]:
    """
    Get a configuration value.

    Priority: environment variable > config file > default

    Args:
        key: Configuration key (e.g., "api-key", "model")

    Returns:
        The configuration value or None if not set
    """
    # Map keys to environment variable names
    env_map = {
        "api-key": "GEMINI_API_KEY",
        "model": "GEMINI_MODEL",
        "default-format": "IMAGE_EDIT_DEFAULT_FORMAT",
        "default-quality": "IMAGE_EDIT_DEFAULT_QUALITY",
    }

    # Check environment variable first
    env_var = env_map.get(key)
    if env_var:
        env_value = os.environ.get(env_var)
        if env_value:
            return env_value

    # Check config file
    config = _load_config_file()
    file_value = config.get(key)
    if file_value is not None:
        return str(file_value)

    # Return default if available
    return DEFAULTS.get(key)


def set_config_value(key: str, value: str) -> None:
    """
    Set a configuration value in the config file.

    Args:
        key: Configuration key
        value: Value to set

    Raises:
        ValueError: If the key is not a valid configuration key
    """
    if key not in CONFIG_KEYS:
        valid_keys = ", ".join(CONFIG_KEYS.keys())
        raise ValueError(f"Unknown configuration key '{key}'. Valid keys: {valid_keys}")

    config = _load_config_file()
    config[key] = value
    _save_config_file(config)


def unset_config_value(key: str) -> bool:
    """
    Remove a configuration value from the config file.

    Args:
        key: Configuration key to remove

    Returns:
        True if the key was removed, False if it wasn't set
    """
    config = _load_config_file()
    if key in config:
        del config[key]
        _save_config_file(config)
        return True
    return False


def get_all_config() -> dict[str, Optional[str]]:
    """
    Get all configuration values with their current effective values.

    Returns:
        Dictionary of all config keys to their current values
    """
    return {key: get_config_value(key) for key in CONFIG_KEYS}


def get_config_file_values() -> dict[str, Any]:
    """Get only the values stored in the config file."""
    return _load_config_file()


# Convenience accessors for common settings
class Settings:
    """Convenience class for accessing settings."""

    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get the Gemini API key."""
        return get_config_value("api-key")

    @property
    def gemini_model(self) -> str:
        """Get the Gemini model name."""
        return get_config_value("model") or DEFAULTS["model"]

    @property
    def default_format(self) -> str:
        """Get the default output format."""
        return get_config_value("default-format") or DEFAULTS["default-format"]

    @property
    def default_quality(self) -> str:
        """Get the default quality setting."""
        return get_config_value("default-quality") or DEFAULTS["default-quality"]

    @property
    def has_gemini_key(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.gemini_api_key)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings (clears cached instance)."""
    global _settings
    _settings = Settings()
    return _settings
