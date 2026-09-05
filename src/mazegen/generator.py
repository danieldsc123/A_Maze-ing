"""Reusable maze-generation boundary owned by the core domain."""

from mazegen.models import Maze, MazeConfig


class MazeGenerator:
    """Generate mazes from validated configuration.

    The generation algorithms will be implemented on their dedicated feature
    branches. Keeping this public contract stable lets the CLI, renderer and
    serializer evolve independently.
    """

    def __init__(self, config: MazeConfig) -> None:
        """Store the validated generation configuration."""
        self.config = config

    def generate(self) -> Maze:
        """Create and return the initial fully walled maze."""
        return Maze.fully_walled(self.config)
