"""Orquestração da aplicação separada da lógica de domínio."""

import sys
from dataclasses import replace
from secrets import randbits
from pathlib import Path
from typing import Sequence

from mazegen.config import load_config
from mazegen.errors import MazeError
from mazegen.generator import MazeGenerator
from mazegen.renderer import TerminalRenderer
from mazegen.models import Maze
from mazegen.serializer import write_maze


def main(
    arguments: Sequence[str] | None = None,
) -> int:
    """Execute a aplicação e converta falhas esperadas em mensagens claras."""
    args = list(sys.argv[1:] if arguments is None else arguments)
    if len(args) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 2

    try:
        config = load_config(Path(args[0]))
        maze = MazeGenerator(config).generate()
        write_maze(maze, config.output_file)

        def regenerate() -> Maze:
            """Gere com uma nova seed e mantenha a saída sincronizada."""
            new_config = replace(config, seed=randbits(64))
            new_maze = MazeGenerator(new_config).generate()
            write_maze(new_maze, new_config.output_file)
            return new_maze

        TerminalRenderer().run(maze, regenerate)
    except (MazeError, OSError, ValueError, NotImplementedError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0
