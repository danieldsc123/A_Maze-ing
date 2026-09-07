"""Serialização da saída hexadecimal do labirinto."""

from pathlib import Path

from mazegen.models import Maze


def write_maze(maze: Maze, destination: Path) -> None:
    """Escreva paredes, linha vazia, entrada, saída e solução com LF."""
    rows = ["".join(format(int(cell.walls), "X") for cell in row)
            for row in maze.cells]
    entry, exit_cell = maze.config.entry, maze.config.exit
    rows.extend(["", f"{entry.x},{entry.y}", f"{exit_cell.x},{exit_cell.y}",
                 maze.solution_directions()])
    with destination.open("w", encoding="utf-8", newline="\n") as output:
        output.write("\n".join(rows) + "\n")
