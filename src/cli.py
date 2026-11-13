"""Command-line interface for the dependency visualizer."""

import argparse
import sys
from typing import List, Optional

from src.config_loader import ConfigError, load_config

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


def main(argv: Optional[List[str]] = None) -> int:
    """Run the main CLI application."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print(f"Configuration Error: {err}", file=sys.stderr)
        return EXIT_ERROR

    for key, value in config.items():
        print(f"{key} = {value}")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())