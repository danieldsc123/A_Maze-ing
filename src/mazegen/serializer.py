"""Hexadecimal output serialization boundary."""

from pathlib import Path

from mazegen.models import Maze


def write_maze(maze: Maze, destination: Path) -> None:
    """Write a maze using the subject's hexadecimal wall encoding."""
    raise NotImplementedError("Maze serialization is not implemented yet")
