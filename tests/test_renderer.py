"""Validação da imagem e das interações do usuário."""
from pathlib import Path
from unittest.mock import patch

import pytest

from mazegen.models import Coordinate, Maze, MazeConfig, Wall
from mazegen.renderer import TerminalRenderer


def sample() -> Maze:
    """Crie um corredor com entrada e saída."""
    config = MazeConfig(3, 1, Coordinate(0, 0), Coordinate(2, 0),
                        Path("unused"), True)
    maze = Maze.fully_walled(config)
    maze.remove_wall(Coordinate(0, 0), Wall.EAST)
    maze.remove_wall(Coordinate(1, 0), Wall.EAST)
    maze.solution = [Coordinate(x, 0) for x in range(3)]
    return maze


def test_render() -> None:
    """Preserve paredes e marcadores ao alternar solução e cores."""
    maze = sample()
    renderer = TerminalRenderer()
    assert renderer.render(maze) == (
        "+---+---+---+\n| E       X |\n+---+---+---+")
    assert "*" in renderer.render(maze, True)
    assert "\033[36m" in renderer.render(maze, color=1)
    assert "*" not in renderer.render(maze)


def test_interactions(capsys: pytest.CaptureFixture[str]) -> None:
    """Exercite solução, cor, regeneração e saída em uma sessão."""
    maze = sample()
    with patch("sys.stdin.isatty", return_value=True), \
            patch("sys.stdout.isatty", return_value=True), \
            patch("builtins.input", side_effect=["s", "c", "r", "q"]), \
            patch.object(TerminalRenderer, "render") as render:
        with patch(__name__ + ".sample", return_value=maze) as regenerate:
            TerminalRenderer().run(maze, regenerate)
            regenerate.assert_called_once()
        assert render.call_args_list[1].args[1] is True
        assert render.call_args_list[2].args[2] == 1


def test_non_interactive(capsys: pytest.CaptureFixture[str]) -> None:
    """Não solicite entrada nem imprima escapes fora de um terminal."""
    with patch("sys.stdin.isatty", return_value=False), \
            patch("builtins.input") as read:
        TerminalRenderer().run(sample())
        read.assert_not_called()
    assert "\033" not in capsys.readouterr().out
