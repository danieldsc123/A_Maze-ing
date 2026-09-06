"""Testes do gerador reutilizável de labirintos."""

from pathlib import Path
from warnings import catch_warnings, simplefilter

from mazegen.errors import GenerationError
from mazegen.generator import MazeGenerator
from mazegen.models import Coordinate, Maze, MazeConfig, Wall


def test_generate_returns_grid_with_requested_dimensions() -> None:
    """Gere um grid com as dimensões configuradas."""
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
    """Retorne apenas vizinhas válidas ainda não visitadas."""
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
    """Construa uma árvore geradora contendo todas as células."""
    config = _config(width=8, height=6, seed=42, perfect=True)

    maze = MazeGenerator(config).generate()

    reachable = _reachable_cells(maze, config.entry)
    assert len(reachable) == config.width * config.height
    assert maze.open_edge_count() == config.width * config.height - 1


def test_same_seed_produces_same_maze() -> None:
    """Gere paredes idênticas com parâmetros e seed idênticos."""
    config = _config(width=8, height=6, seed=123, perfect=True)

    first = MazeGenerator(config).generate()
    second = MazeGenerator(config).generate()

    assert _wall_signature(first) == _wall_signature(second)


def test_different_seeds_produce_different_mazes() -> None:
    """Permita que seeds diferentes escolham percursos diferentes."""
    first = MazeGenerator(_config(seed=1, perfect=True)).generate()
    second = MazeGenerator(_config(seed=2, perfect=True)).generate()

    assert _wall_signature(first) != _wall_signature(second)


def test_solution_connects_entry_to_exit_through_passages() -> None:
    """Armazene um caminho válido e exponha suas direções cardeais."""
    config = _config(width=7, height=5, seed=42, perfect=True)

    maze = MazeGenerator(config).generate()

    assert maze.solution[0] == config.entry
    assert maze.solution[-1] == config.exit
    assert len(maze.solution_directions()) == len(maze.solution) - 1
    for current, following in zip(maze.solution, maze.solution[1:]):
        assert following in maze.passage_neighbors(current)


def test_generator_rejects_invalid_parameters() -> None:
    """Rejeite dimensões e coordenadas de entrada ou saída impossíveis."""
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


def test_large_maze_contains_closed_42_pattern() -> None:
    """Mantenha fechadas todas as células do padrão visual."""
    config = _config(width=20, height=15, seed=42, perfect=True)

    maze = MazeGenerator(config).generate()

    assert maze.pattern_cells
    assert config.entry not in maze.pattern_cells
    assert config.exit not in maze.pattern_cells
    assert all(
        int(maze.cell_at(coordinate).walls) == 0xF
        for coordinate in maze.pattern_cells
    )
    reachable = _reachable_cells(maze, config.entry)
    expected = config.width * config.height - len(maze.pattern_cells)
    assert len(reachable) == expected
    assert maze.open_edge_count() == expected - 1


def test_small_maze_omits_pattern_with_console_warning() -> None:
    """Avise sem falhar quando o padrão 42 não couber."""
    config = _config(width=8, height=6, perfect=True)

    with catch_warnings(record=True) as warnings:
        simplefilter("always")
        maze = MazeGenerator(config).generate()

    assert not maze.pattern_cells
    assert any("too small" in str(item.message) for item in warnings)


def test_non_perfect_maze_is_a_connected_pacman_board() -> None:
    """Crie loops, abra posições principais e mantenha poucos becos."""
    config = _config(width=20, height=15, seed=42, perfect=False)

    maze = MazeGenerator(config).generate()

    assert len(_reachable_cells(maze, config.entry)) == len(
        maze.traversable_cells()
    )
    assert maze.cycle_count() >= 2
    assert len(maze.dead_ends()) <= 2
    assert not maze.has_open_3x3_area()

    required_corridors = {
        Coordinate(0, 0),
        Coordinate(config.width - 1, 0),
        Coordinate(0, config.height - 1),
        Coordinate(config.width - 1, config.height - 1),
        Coordinate(config.width // 2, config.height // 2),
    }
    assert not required_corridors & maze.pattern_cells
    assert all(
        len(maze.passage_neighbors(coordinate)) >= 2
        for coordinate in required_corridors
    )


def test_non_perfect_mode_is_reproducible() -> None:
    """Use a seed configurada para escavar e trançar o labirinto."""
    config = _config(width=20, height=15, seed=84, perfect=False)

    first = MazeGenerator(config).generate()
    second = MazeGenerator(config).generate()

    assert _wall_signature(first) == _wall_signature(second)


def _config(
    width: int = 6,
    height: int = 5,
    seed: int | None = 42,
    perfect: bool = True,
    entry: Coordinate = Coordinate(0, 0),
    exit_coordinate: Coordinate | None = None,
) -> MazeConfig:
    """Construa uma configuração válida para os testes do gerador."""
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
    """Retorne todas as células alcançáveis a partir de uma coordenada."""
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
    """Converta paredes em um valor imutável para comparações."""
    return tuple(tuple(int(cell.walls) for cell in row) for row in maze.cells)
