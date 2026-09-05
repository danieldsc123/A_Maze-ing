"""Tests for the reusable maze generator."""

from pathlib import Path

from mazegen.generator import MazeGenerator
from mazegen.models import Coordinate, MazeConfig, Wall


def test_generate_returns_fully_walled_grid() -> None:
    """Start generation with a fully closed grid."""
    config = MazeConfig(
        width=3,
        height=2,
        entry=Coordinate(0, 0),
        exit=Coordinate(2, 1),
        output_file=Path("maze.txt"),
        seed=42,
    )

    maze = MazeGenerator(config).generate()

    assert len(maze.cells) == 2
    assert all(len(row) == 3 for row in maze.cells)

    all_walls = Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST
    assert all(
        cell.walls == all_walls
        for row in maze.cells
        for cell in row
    )
