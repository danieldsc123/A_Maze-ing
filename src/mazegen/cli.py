"""Orquestração da aplicação separada da lógica de domínio."""

import sys
from pathlib import Path
from typing import Sequence

from mazegen.config import load_config
from mazegen.errors import MazeError
from mazegen.generator import MazeGenerator
from mazegen.renderer import TerminalRenderer
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
        TerminalRenderer().run(maze)
    except (MazeError, OSError, ValueError, NotImplementedError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0
