"""Configuration parsing and validation boundary."""

from pathlib import Path

from mazegen.errors import ConfigurationError
from mazegen.models import MazeConfig


def load_config(path: Path) -> MazeConfig:
    """Load and validate a KEY=VALUE configuration file.

    The complete parser belongs to its dedicated feature branch.
    """
    if not path.is_file():
        raise ConfigurationError(f"Configuration file not found: {path}")
    raise ConfigurationError("Configuration parsing is not implemented yet")
