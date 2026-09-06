"""Fronteira da serialização da saída hexadecimal."""

from pathlib import Path

from mazegen.models import Maze


def write_maze(maze: Maze, destination: Path) -> None:
    """Escreva o labirinto usando a codificação hexadecimal do subject."""
    raise NotImplementedError("Maze serialization is not implemented yet")
