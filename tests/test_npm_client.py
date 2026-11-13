"""Unit tests for npm registry client."""

import unittest
from unittest.mock import patch

from src.npm_client import (
    NpmClientError,
    build_package_url,
    extract_dependencies,
    get_direct_dependencies,
)


class TestNpmClient(unittest.TestCase):
    """Test cases for fetching and parsing npm package data."""

    def test_build_package_url(self) -> None:
        """Test URL construction for standard npm package."""
        url = build_package_url(
            "https://registry.npmjs.org/", "express", "4.18.2"
        )
        self.assertEqual(
            url, "https://registry.npmjs.org/express/4.18.2"
        )

    def test_extract_direct_dependencies(self) -> None:
        """Test extracting dependencies from version endpoint JSON."""
        mock_data = {
            "name": "express",
            "version": "4.18.2",
            "dependencies": {"accepts": "~1.3.8", "cookie": "0.5.0"},
        }
        deps = extract_dependencies(mock_data, "4.18.2")
        self.assertEqual(
            deps, {"accepts": "~1.3.8", "cookie": "0.5.0"}
        )

    def test_extract_nested_version_dependencies(self) -> None:
        """Test extracting dependencies from full package JSON."""
        mock_data = {
            "name": "demo",
            "versions": {
                "1.0.0": {"dependencies": {"lodash": "^4.17.21"}}
            },
        }
        deps = extract_dependencies(mock_data, "1.0.0")
        self.assertEqual(deps, {"lodash": "^4.17.21"})

    def test_extract_missing_version_raises(self) -> None:
        """Test error when version is missing in full package JSON."""
        mock_data = {"name": "demo", "versions": {"1.0.0": {}}}
        with self.assertRaises(NpmClientError):
            extract_dependencies(mock_data, "2.0.0")

    def test_extract_no_dependencies(self) -> None:
        """Test package with no dependencies returns empty dict."""
        mock_data = {"name": "empty-pkg", "version": "1.0.0"}
        deps = extract_dependencies(mock_data, "1.0.0")
        self.assertEqual(deps, {})

    @patch("src.npm_client.fetch_json")
    def test_get_direct_dependencies(self, 
                        mock_fetch: unittest.mock.MagicMock) -> None:
        """Test high-level dependency retrieval with mocked network."""
        mock_fetch.return_value = {
            "dependencies": {"debug": "2.6.9"}
        }
        deps = get_direct_dependencies(
            "https://registry.npmjs.org", "express", "4.18.2"
        )
        self.assertEqual(deps, {"debug": "2.6.9"})


if __name__ == "__main__":
    unittest.main()