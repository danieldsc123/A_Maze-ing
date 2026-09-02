"""Tests for the maze data structures."""

from pathlib import Path

from mazegen.models import Cell, Coordinate, Maze, MazeConfig, Wall


def test_wall_values_use_independent_bits() -> None:
    """Represent each wall with one independent bit."""
    assert Wall.NORTH == 1
    assert Wall.EAST == 2
    assert Wall.SOUTH == 4
    assert Wall.WEST == 8


def test_all_walls_form_hexadecimal_f() -> None:
    """Combine the four walls into the hexadecimal value F."""
    walls = Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST

    assert int(walls) == 0xF


def test_cell_starts_without_walls() -> None:
    """Create an open cell by default."""
    cell = Cell()

    assert cell.walls == Wall(0)


def test_cell_can_add_and_check_a_wall() -> None:
    """Add a wall without affecting the other directions."""
    cell = Cell()

    cell.add_wall(Wall.NORTH)

    assert cell.has_wall(Wall.NORTH)
    assert not cell.has_wall(Wall.SOUTH)


def test_cell_can_remove_a_wall() -> None:
    """Remove one wall while preserving the remaining walls."""
    cell = Cell(Wall.NORTH | Wall.EAST)

    cell.remove_wall(Wall.NORTH)

    assert not cell.has_wall(Wall.NORTH)
    assert cell.has_wall(Wall.EAST)


def test_maze_stores_a_grid_of_cells() -> None:
    """Store cells using rows and columns."""
    config = MazeConfig(
        width=2,
        height=2,
        entry=Coordinate(0, 0),
        exit=Coordinate(1, 1),
        output_file=Path("maze.txt"),
    )
    cells = [
        [Cell(), Cell()],
        [Cell(), Cell()],
    ]

    maze = Maze(config=config, cells=cells)

    assert len(maze.cells) == 2
    assert len(maze.cells[0]) == 2
    assert isinstance(maze.cells[0][0], Cell)
    assert maze.solution == []
