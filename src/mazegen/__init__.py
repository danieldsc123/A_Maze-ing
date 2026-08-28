"""Reusable maze-generation package."""

from mazegen.generator import MazeGenerator
from mazegen.models import Coordinate, Maze, MazeConfig

__all__ = ["Coordinate", "Maze", "MazeConfig", "MazeGenerator"]
__version__ = "0.1.0"
