"""Unit tests for configuration loading and validation."""

import tempfile
from typing import Any, Dict
import unittest

from src.config_loader import ConfigError, load_config, validate_config


def get_valid_dict() -> Dict[str, Any]:
    """Return a valid configuration dictionary for testing."""
    return {
        "package_name": "express",
        "repo_url_or_path": "https://registry.npmjs.org",
        "test_repo_mode": False,
        "package_version": "4.18.2",
        "output_image": "graph.png",
        "max_depth": 3,
        "filter_substring": "dev",
    }


class TestConfigValidation(unittest.TestCase):
    """Test cases for validating configuration parameters."""

    def test_valid_config(self) -> None:
        """Test that a valid configuration passes validation."""
        data = get_valid_dict()
        result = validate_config(data)
        self.assertEqual(result["package_name"], "express")
        self.assertEqual(result["max_depth"], 3)

    def test_missing_parameter(self) -> None:
        """Test error when a required parameter is missing."""
        data = get_valid_dict()
        del data["package_name"]
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_package_name(self) -> None:
        """Test error on empty or non-string package_name."""
        data = get_valid_dict()
        data["package_name"] = "   "
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_repo_url(self) -> None:
        """Test error on invalid repo_url_or_path."""
        data = get_valid_dict()
        data["repo_url_or_path"] = 12345
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_test_repo_mode(self) -> None:
        """Test error when test_repo_mode is not a boolean."""
        data = get_valid_dict()
        data["test_repo_mode"] = "false"
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_package_version(self) -> None:
        """Test error on empty package_version."""
        data = get_valid_dict()
        data["package_version"] = ""
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_output_image(self) -> None:
        """Test error on empty output_image."""
        data = get_valid_dict()
        data["output_image"] = ""
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_max_depth_negative(self) -> None:
        """Test error when max_depth is negative."""
        data = get_valid_dict()
        data["max_depth"] = -1
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_max_depth_bool(self) -> None:
        """Test error when max_depth is a boolean instead of int."""
        data = get_valid_dict()
        data["max_depth"] = True
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_invalid_filter_substring(self) -> None:
        """Test error when filter_substring is not a string."""
        data = get_valid_dict()
        data["filter_substring"] = None
        with self.assertRaises(ConfigError):
            validate_config(data)

    def test_file_not_found(self) -> None:
        """Test error when TOML file does not exist."""
        with self.assertRaises(ConfigError):
            load_config("non_existent_file.toml")

    def test_invalid_toml_syntax(self) -> None:
        """Test error when TOML file has broken syntax."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as tmp:
            tmp.write("invalid_toml = [unclosed")
            tmp_path = tmp.name

        with self.assertRaises(ConfigError):
            load_config(tmp_path)


if __name__ == "__main__":
    unittest.main()