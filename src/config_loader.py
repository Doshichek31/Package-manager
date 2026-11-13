"""Module for loading and validating TOML configuration."""

from pathlib import Path
import tomllib
from typing import Any, Dict

MIN_DEPTH = 0


class ConfigError(Exception):
    """Custom exception for configuration validation errors."""


def _get_key(data: Dict[str, Any], key: str) -> Any:
    """Retrieve a key from dictionary or raise ConfigError."""
    if key not in data:
        raise ConfigError(f"Missing required parameter: '{key}'")
    return data[key]


def _validate_non_empty_str(data: Dict[str, Any], key: str) -> str:
    """Validate that the parameter is a non-empty string."""
    val = _get_key(data, key)
    if not isinstance(val, str) or not val.strip():
        raise ConfigError(
            f"Parameter '{key}' must be a non-empty string."
        )
    return val.strip()


def _validate_str(data: Dict[str, Any], key: str) -> str:
    """Validate that the parameter is a string."""
    val = _get_key(data, key)
    if not isinstance(val, str):
        raise ConfigError(f"Parameter '{key}' must be a string.")
    return val


def _validate_bool(data: Dict[str, Any], key: str) -> bool:
    """Validate that the parameter is a boolean."""
    val = _get_key(data, key)
    if not isinstance(val, bool):
        raise ConfigError(f"Parameter '{key}' must be a boolean.")
    return val


def _validate_depth(data: Dict[str, Any], key: str) -> int:
    """Validate that the parameter is a non-negative integer."""
    val = _get_key(data, key)
    if isinstance(val, bool) or not isinstance(val, int):
        raise ConfigError(f"Parameter '{key}' must be an integer.")
    if val < MIN_DEPTH:
        raise ConfigError(
            f"Parameter '{key}' must be >= {MIN_DEPTH}."
        )
    return val


def validate_config(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate all required configuration parameters."""
    return {
        "package_name": _validate_non_empty_str(
            raw_data, "package_name"
        ),
        "repo_url_or_path": _validate_non_empty_str(
            raw_data, "repo_url_or_path"
        ),
        "test_repo_mode": _validate_bool(
            raw_data, "test_repo_mode"
        ),
        "package_version": _validate_non_empty_str(
            raw_data, "package_version"
        ),
        "output_image": _validate_non_empty_str(
            raw_data, "output_image"
        ),
        "max_depth": _validate_depth(raw_data, "max_depth"),
        "filter_substring": _validate_str(
            raw_data, "filter_substring"
        ),
    }


def load_config(file_path: str) -> Dict[str, Any]:
    """Load and validate configuration from a TOML file."""
    path = Path(file_path)
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {file_path}")
    try:
        with path.open("rb") as file:
            raw_data = tomllib.load(file)
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(f"Invalid TOML format: {err}") from err
    except OSError as err:
        raise ConfigError(f"Error reading file: {err}") from err

    return validate_config(raw_data)