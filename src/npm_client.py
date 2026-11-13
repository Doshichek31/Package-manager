"""Module for fetching npm package dependencies from registry."""

import json
from typing import Any, Dict
import urllib.error
import urllib.parse
import urllib.request

HTTP_TIMEOUT_SECONDS = 10


class NpmClientError(Exception):
    """Exception raised for errors during npm data fetching."""


def build_package_url(
    repo_url: str, package_name: str, version: str
) -> str:
    """Build the npm registry URL for a package and version."""
    base = repo_url.rstrip("/")
    encoded_pkg = urllib.parse.quote(package_name, safe="@/")
    encoded_ver = urllib.parse.quote(version, safe="")
    return f"{base}/{encoded_pkg}/{encoded_ver}"


def fetch_json(url: str) -> Dict[str, Any]:
    """Fetch and parse JSON data from a given URL."""
    req = urllib.request.Request(
        url, headers={"Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(
            req, timeout=HTTP_TIMEOUT_SECONDS
        ) as response:
            raw_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        raise NpmClientError(
            f"HTTP error {err.code} when fetching {url}"
        ) from err
    except urllib.error.URLError as err:
        raise NpmClientError(
            f"Network error when fetching {url}: {err.reason}"
        ) from err
    except OSError as err:
        raise NpmClientError(f"Error fetching {url}: {err}") from err

    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError as err:
        raise NpmClientError(
            f"Invalid JSON received from {url}"
        ) from err

    if not isinstance(data, dict):
        raise NpmClientError("Expected JSON object from registry.")
    return data


def extract_dependencies(
    data: Dict[str, Any], version: str
) -> Dict[str, str]:
    """Extract direct dependencies dictionary from npm metadata."""
    version_data = data
    if "versions" in data and isinstance(data["versions"], dict):
        if version not in data["versions"]:
            raise NpmClientError(
                f"Version '{version}' not found in package data."
            )
        version_data = data["versions"][version]

    deps = version_data.get("dependencies", {})
    if not isinstance(deps, dict):
        return {}
    return {str(k): str(v) for k, v in deps.items()}


def get_direct_dependencies(
    repo_url: str, package_name: str, version: str
) -> Dict[str, str]:
    """Fetch direct dependencies for a specific npm package version."""
    url = build_package_url(repo_url, package_name, version)
    data = fetch_json(url)
    return extract_dependencies(data, version)