"""Domain-specific exceptions exposed by the package."""


class MazeError(Exception):
    """Base exception for errors that can be shown safely to the user."""


class ConfigurationError(MazeError):
    """Raised when a configuration file or value is invalid."""


class GenerationError(MazeError):
    """Raised when a maze cannot be generated with the requested parameters."""
