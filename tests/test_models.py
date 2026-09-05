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


def test_fully_walled_maze_starts_with_hexadecimal_f() -> None:
    """Initialize every cell with all walls closed."""
    maze = Maze.fully_walled(_config())

    assert all(int(cell.walls) == 0xF for row in maze.cells for cell in row)
    assert maze.has_consistent_walls()


def test_remove_wall_updates_both_neighbouring_cells() -> None:
    """Keep shared walls coherent when opening a passage."""
    maze = Maze.fully_walled(_config())

    maze.remove_wall(Coordinate(0, 0), Wall.EAST)

    assert not maze.cell_at(Coordinate(0, 0)).has_wall(Wall.EAST)
    assert not maze.cell_at(Coordinate(1, 0)).has_wall(Wall.WEST)
    assert maze.has_consistent_walls()


def test_add_wall_updates_both_neighbouring_cells() -> None:
    """Keep shared walls coherent when closing a passage."""
    maze = Maze.fully_walled(_config())
    maze.remove_wall(Coordinate(0, 0), Wall.SOUTH)

    maze.add_wall(Coordinate(0, 0), Wall.SOUTH)

    assert maze.cell_at(Coordinate(0, 0)).has_wall(Wall.SOUTH)
    assert maze.cell_at(Coordinate(0, 1)).has_wall(Wall.NORTH)


def test_external_border_cannot_be_removed() -> None:
    """Keep the maze closed at its external border."""
    maze = Maze.fully_walled(_config())

    try:
        maze.remove_wall(Coordinate(0, 0), Wall.NORTH)
    except ValueError as error:
        assert "external border" in str(error)
    else:
        raise AssertionError("Expected external border removal to fail")


def test_consistency_check_detects_asymmetric_shared_wall() -> None:
    """Detect wall data changed without the maze mutation API."""
    maze = Maze.fully_walled(_config())

    maze.cell_at(Coordinate(0, 0)).remove_wall(Wall.EAST)

    assert not maze.has_consistent_walls()


def test_consistency_check_detects_open_external_border() -> None:
    """Detect an invalid opening at the outside of the grid."""
    maze = Maze.fully_walled(_config())

    maze.cell_at(Coordinate(0, 0)).remove_wall(Wall.NORTH)

    assert not maze.has_consistent_walls()


def test_cell_at_rejects_coordinate_outside_grid() -> None:
    """Reject negative and overflowing coordinates."""
    maze = Maze.fully_walled(_config())

    for coordinate in (Coordinate(-1, 0), Coordinate(2, 1)):
        try:
            maze.cell_at(coordinate)
        except IndexError:
            pass
        else:
            raise AssertionError("Expected coordinate outside maze to fail")


def test_directional_operation_rejects_combined_wall_flags() -> None:
    """Require one direction when changing a shared wall."""
    maze = Maze.fully_walled(_config())

    try:
        maze.remove_wall(Coordinate(0, 0), Wall.EAST | Wall.SOUTH)
    except ValueError as error:
        assert "one cardinal wall" in str(error)
    else:
        raise AssertionError("Expected combined wall flags to fail")


def _config() -> MazeConfig:
    """Return a small valid configuration for model tests."""
    return MazeConfig(
        width=2,
        height=2,
        entry=Coordinate(0, 0),
        exit=Coordinate(1, 1),
        output_file=Path("maze.txt"),
    )
