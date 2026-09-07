"""Visualização ASCII e interações no terminal."""

import sys
from typing import Callable

from mazegen.errors import MazeError
from mazegen.models import Coordinate, Maze, Wall


COLORS = ("37", "36", "33", "32", "35", "34", "31")


class TerminalRenderer:
    """Mostre paredes, entrada, saída, padrão 42 e solução opcional."""

    def render(self, maze: Maze, show_solution: bool = False,
               color: int | None = None) -> str:
        """Construa uma imagem textual sem alterar o labirinto."""
        canvas = [[" "] * (maze.config.width * 4 + 1)
                  for _ in range(maze.config.height * 2 + 1)]
        solution = set(maze.solution) if show_solution else set()
        for y, row in enumerate(maze.cells):
            for x, cell in enumerate(row):
                top, left = y * 2, x * 4
                for dy in (0, 2):
                    for dx in (0, 4):
                        canvas[top + dy][left + dx] = "+"
                for wall, dy in ((Wall.NORTH, 0), (Wall.SOUTH, 2)):
                    if cell.has_wall(wall):
                        canvas[top + dy][left + 1:left + 4] = list("---")
                for wall, dx in ((Wall.WEST, 0), (Wall.EAST, 4)):
                    if cell.has_wall(wall):
                        canvas[top + 1][left + dx] = "|"
                coordinate = Coordinate(x, y)
                symbol = "*" if coordinate in solution else " "
                if coordinate in maze.pattern_cells:
                    canvas[top + 1][left + 1:left + 4] = list("###")
                else:
                    if coordinate == maze.config.entry:
                        symbol = "E"
                    elif coordinate == maze.config.exit:
                        symbol = "X"
                    canvas[top + 1][left + 2] = symbol
        if show_solution:
            for current, following in zip(maze.solution, maze.solution[1:]):
                x, y = current.x * 4 + 2, current.y * 2 + 1
                target_x = following.x * 4 + 2
                target_y = following.y * 2 + 1
                dx = (target_x > x) - (target_x < x)
                dy = (target_y > y) - (target_y < y)
                while (x, y) != (target_x, target_y):
                    if canvas[y][x] == " ":
                        canvas[y][x] = "*"
                    x, y = x + dx, y + dy
        lines = ["".join(row) for row in canvas]
        if color is not None:
            escape = f"\033[{COLORS[color % len(COLORS)]}m"
            palette = {"E": "\033[95m", "X": "\033[91m",
                       "#": "\033[97m", "*": "\033[96m"}
            palette.update({symbol: escape for symbol in "+-|"})
            lines = ["".join(f"{palette[c]}{c}\033[0m" if c in palette else c
                             for c in line) for line in lines]
        return "\n".join(lines)

    def run(self, maze: Maze,
            regenerate: Callable[[], Maze] | None = None) -> None:
        """Leia comandos por linha; sem TTY, imprima uma imagem e termine."""
        interactive = sys.stdin.isatty() and sys.stdout.isatty()
        if not interactive:
            print(self.render(maze))
            return
        show_solution, color = False, 0
        message = ""
        while True:
            print("\033[2J\033[H", end="")
            print(self.render(maze, show_solution, color))
            print("E: entrada | X: saída | #: padrão 42 | *: solução")
            print("[r] regenerar  [s] solução  [c] cores  [q] sair")
            if message:
                print(message)
            message = ""
            try:
                command = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if command == "q":
                return
            if command == "s":
                show_solution = not show_solution
            elif command == "c":
                color = (color + 1) % len(COLORS)
            elif command == "r":
                if regenerate is None:
                    message = "Regeneração indisponível nesta sessão."
                    continue
                try:
                    maze = regenerate()
                except (MazeError, OSError, ValueError) as error:
                    message = f"Não foi possível regenerar: {error}"
            else:
                message = "Use r, s, c ou q e pressione Enter."
