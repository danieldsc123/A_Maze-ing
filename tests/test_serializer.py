"""Verificação independente do formato exportado."""
from pathlib import Path

import pytest

from mazegen.generator import MazeGenerator
from mazegen.models import Coordinate, Maze, MazeConfig, Wall
from mazegen.serializer import write_maze


def test_exact_output(tmp_path: Path) -> None:
    """Compare bytes de um labirinto pequeno com formato conhecido."""
    path = tmp_path / "maze.txt"
    config = MazeConfig(2, 1, Coordinate(0, 0), Coordinate(1, 0), path, True)
    maze = Maze.fully_walled(config)
    maze.remove_wall(config.entry, Wall.EAST)
    maze.solution = [config.entry, config.exit]
    write_maze(maze, path)
    assert path.read_bytes() == b"D7\n\n0,0\n1,0\nE\n"


@pytest.mark.parametrize("perfect", [True, False])
def test_exported_solution(tmp_path: Path, perfect: bool) -> None:
    """Percorra a solução usando apenas os bits do arquivo exportado."""
    path = tmp_path / "maze.txt"
    config = MazeConfig(20, 15, Coordinate(0, 0), Coordinate(19, 14),
                        path, perfect, 42)
    write_maze(MazeGenerator(config).generate(), path)
    lines = path.read_text().splitlines()
    assert len(lines) == config.height + 4
    assert all(len(row) == config.width for row in lines[:config.height])
    assert lines[config.height] == ""
    moves = {"N": (0, -1, 1), "E": (1, 0, 2),
             "S": (0, 1, 4), "W": (-1, 0, 8)}
    x, y = map(int, lines[-3].split(","))
    for direction in lines[-1]:
        dx, dy, wall = moves[direction]
        assert not int(lines[y][x], 16) & wall
        x, y = x + dx, y + dy
        assert 0 <= x < config.width and 0 <= y < config.height
    assert f"{x},{y}" == lines[-2]
