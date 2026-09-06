"""Tests for the reusable maze generator."""

from pathlib import Path

from mazegen.errors import GenerationError
from mazegen.generator import MazeGenerator
from mazegen.models import Coordinate, Maze, MazeConfig, Wall


def test_generate_returns_grid_with_requested_dimensions() -> None:
    """Generate a grid with the configured dimensions."""
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

    assert maze.has_consistent_walls()


def test_unvisited_neighbors_excludes_visited_and_outside_cells() -> None:
    """Return only valid neighbouring cells that were not visited."""
    config = MazeConfig(
        width=3,
        height=3,
        entry=Coordinate(0, 0),
        exit=Coordinate(2, 2),
        output_file=Path("maze.txt"),
        seed=42,
    )
    generator = MazeGenerator(config)
    visited = {Coordinate(0, 0)}

    neighbors = generator._unvisited_neighbors(
        Coordinate(1, 0),
        visited,
    )

    assert set(neighbors) == {
        (Coordinate(2, 0), Wall.EAST),
        (Coordinate(1, 1), Wall.SOUTH),
    }


def test_perfect_maze_is_connected_and_has_no_loops() -> None:
    """Build a spanning tree containing every cell."""
    config = _config(width=8, height=6, seed=42, perfect=True)

    maze = MazeGenerator(config).generate()

    reachable = _reachable_cells(maze, config.entry)
    assert len(reachable) == config.width * config.height
    assert maze.open_edge_count() == config.width * config.height - 1


def test_same_seed_produces_same_maze() -> None:
    """Generate identical walls from identical parameters and seed."""
    config = _config(width=8, height=6, seed=123, perfect=True)

    first = MazeGenerator(config).generate()
    second = MazeGenerator(config).generate()

    assert _wall_signature(first) == _wall_signature(second)


def test_different_seeds_produce_different_mazes() -> None:
    """Allow distinct seeds to select different traversal routes."""
    first = MazeGenerator(_config(seed=1, perfect=True)).generate()
    second = MazeGenerator(_config(seed=2, perfect=True)).generate()

    assert _wall_signature(first) != _wall_signature(second)


def test_solution_connects_entry_to_exit_through_passages() -> None:
    """Store a valid path and expose its cardinal direction encoding."""
    config = _config(width=7, height=5, seed=42, perfect=True)

    maze = MazeGenerator(config).generate()

    assert maze.solution[0] == config.entry
    assert maze.solution[-1] == config.exit
    assert len(maze.solution_directions()) == len(maze.solution) - 1
    for current, following in zip(maze.solution, maze.solution[1:]):
        assert following in maze.passage_neighbors(current)


def test_generator_rejects_invalid_parameters() -> None:
    """Reject impossible dimensions and entry/exit coordinates."""
    invalid_configs = (
        _config(width=0),
        _config(entry=Coordinate(-1, 0)),
        _config(exit_coordinate=Coordinate(20, 20)),
        _config(entry=Coordinate(0, 0), exit_coordinate=Coordinate(0, 0)),
    )

    for config in invalid_configs:
        try:
            MazeGenerator(config).generate()
        except GenerationError as error:
            assert str(error)
        else:
            raise AssertionError("Expected invalid maze configuration to fail")


def _config(
    width: int = 6,
    height: int = 5,
    seed: int | None = 42,
    perfect: bool = True,
    entry: Coordinate = Coordinate(0, 0),
    exit_coordinate: Coordinate | None = None,
) -> MazeConfig:
    """Build a valid generator configuration for tests."""
    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_coordinate or Coordinate(width - 1, height - 1),
        output_file=Path("maze.txt"),
        perfect=perfect,
        seed=seed,
    )


def _reachable_cells(maze: Maze, start: Coordinate) -> set[Coordinate]:
    """Return all cells reachable from a starting coordinate."""
    pending = [start]
    visited = {start}
    while pending:
        current = pending.pop()
        for neighbor in maze.passage_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                pending.append(neighbor)
    return visited


def _wall_signature(maze: Maze) -> tuple[tuple[int, ...], ...]:
    """Convert maze walls into an immutable value for comparisons."""
    return tuple(tuple(int(cell.walls) for cell in row) for row in maze.cells)
