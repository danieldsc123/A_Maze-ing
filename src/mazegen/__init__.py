"""Pacote reutilizável de geração de labirintos."""

from mazegen.generator import MazeGenerator
from mazegen.models import Cell, Coordinate, Maze, MazeConfig, Wall

__all__ = [
    "Cell",
    "Coordinate",
    "Maze",
    "MazeConfig",
    "MazeGenerator",
    "Wall",
]
__version__ = "0.1.0"
