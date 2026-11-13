"""Command-line interface for the dependency visualizer."""

import argparse
import sys
from typing import Dict, List, Optional

from src.config_loader import ConfigError, load_config
from src.npm_client import NpmClientError, get_direct_dependencies

EXIT_SUCCESS = 0
EXIT_ERROR = 1


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Dependency graph visualization tool."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.toml",
        help="Path to the TOML configuration file.",
    )
    return parser.parse_args(args)


def print_dependencies(
    pkg_name: str, pkg_version: str, deps: Dict[str, str]
) -> None:
    """Print direct dependencies of the package to stdout."""
    print(f"Direct dependencies for {pkg_name}@{pkg_version}:")
    if not deps:
        print("  (no direct dependencies)")
        return
    for dep_name, dep_ver in deps.items():
        print(f"  {dep_name}: {dep_ver}")


def main(argv: Optional[List[str]] = None) -> int:
    """Run the main CLI application."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        deps = get_direct_dependencies(
            config["repo_url_or_path"],
            config["package_name"],
            config["package_version"],
        )
    except ConfigError as err:
        print(f"Configuration Error: {err}", file=sys.stderr)
        return EXIT_ERROR
    except NpmClientError as err:
        print(f"Repository Error: {err}", file=sys.stderr)
        return EXIT_ERROR

    print_dependencies(
        config["package_name"], config["package_version"], deps
    )
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())