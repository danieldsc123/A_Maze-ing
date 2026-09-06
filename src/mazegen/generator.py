"""Fronteira reutilizável de geração pertencente ao domínio central."""

from collections import deque
from random import Random
from warnings import warn

from mazegen.errors import GenerationError
from mazegen.models import Coordinate, Maze, MazeConfig, Wall


DIRECTIONS: tuple[tuple[Wall, int, int], ...] = (
    (Wall.NORTH, 0, -1),
    (Wall.EAST, 1, 0),
    (Wall.SOUTH, 0, 1),
    (Wall.WEST, -1, 0),
)

PATTERN_42 = (
    "10001011111",
    "10001000001",
    "10001000001",
    "11111011111",
    "00001010000",
    "00001010000",
    "00001011111",
)
PATTERN_MARGIN = 1


class MazeGenerator:
    """Gere labirintos a partir de uma configuração validada.

    Manter este contrato público estável permite que a CLI, a renderização e a
    serialização evoluam de maneira independente.
    """

    def __init__(self, config: MazeConfig) -> None:
        """Armazene a configuração validada da geração."""
        self.config = config

    def generate(self) -> Maze:
        """Gere um labirinto conectado e sua solução mais curta."""
        self._validate_config()
        maze = Maze.fully_walled(self.config)
        maze.pattern_cells = self._build_pattern_cells()
        random = Random(self.config.seed)
        visited = {self.config.entry}
        stack = [self.config.entry]

        while stack:
            current = stack[-1]
            neighbors = self._unvisited_neighbors(
                current,
                visited,
                maze.pattern_cells,
            )
            if not neighbors:
                stack.pop()
                continue

            neighbor, wall = random.choice(neighbors)
            maze.remove_wall(current, wall)
            visited.add(neighbor)
            stack.append(neighbor)

        expected_cells = (
            self.config.width * self.config.height
            - len(maze.pattern_cells)
        )
        if len(visited) != expected_cells:
            raise GenerationError("Could not connect every maze cell")

        if not self.config.perfect:
            self._braid_maze(maze, random)
        maze.solution = self._shortest_path(maze)
        return maze

    def _unvisited_neighbors(
        self,
        coordinate: Coordinate,
        visited: set[Coordinate],
        blocked: set[Coordinate] | None = None,
    ) -> list[tuple[Coordinate, Wall]]:
        """Retorne células vizinhas válidas que ainda não foram visitadas."""
        unavailable = blocked or set()
        neighbors: list[tuple[Coordinate, Wall]] = []
        for wall, delta_x, delta_y in DIRECTIONS:
            neighbor = Coordinate(
                coordinate.x + delta_x,
                coordinate.y + delta_y,
            )

            inside_grid = (
                0 <= neighbor.x < self.config.width
                and 0 <= neighbor.y < self.config.height
            )

            if (
                inside_grid
                and neighbor not in visited
                and neighbor not in unavailable
            ):
                neighbors.append((neighbor, wall))

        return neighbors

    def _build_pattern_cells(self) -> set[Coordinate]:
        """Posicione um 42 de células fechadas quando houver espaço."""
        pattern_height = len(PATTERN_42)
        pattern_width = len(PATTERN_42[0])
        minimum_width = pattern_width + 2 * PATTERN_MARGIN
        minimum_height = pattern_height + 2 * PATTERN_MARGIN
        if (
            self.config.width < minimum_width
            or self.config.height < minimum_height
        ):
            warn(
                "Maze is too small to contain the 42 pattern; omitting it",
                UserWarning,
                stacklevel=2,
            )
            return set()

        centered_x = (self.config.width - pattern_width) // 2
        centered_y = (self.config.height - pattern_height) // 2
        origins = [
            (x, y)
            for y in range(
                PATTERN_MARGIN,
                self.config.height - pattern_height,
            )
            for x in range(
                PATTERN_MARGIN,
                self.config.width - pattern_width,
            )
        ]
        origins.sort(
            key=lambda origin: (
                abs(origin[0] - centered_x) + abs(origin[1] - centered_y),
                origin[1],
                origin[0],
            )
        )

        protected = {self.config.entry, self.config.exit}
        if not self.config.perfect:
            protected.update(self._pacman_positions())

        for origin_x, origin_y in origins:
            cells = {
                Coordinate(origin_x + x, origin_y + y)
                for y, row in enumerate(PATTERN_42)
                for x, value in enumerate(row)
                if value == "1"
            }
            if not cells & protected:
                return cells

        warn(
            "No valid placement for the 42 pattern; omitting it",
            UserWarning,
            stacklevel=2,
        )
        return set()

    def _braid_maze(self, maze: Maze, random: Random) -> None:
        """Adicione loops seguros e reduza becos sem saída no modo Pac-Man."""
        targets = list(maze.dead_ends() | self._pacman_positions())
        random.shuffle(targets)
        for coordinate in targets:
            while len(maze.passage_neighbors(coordinate)) < 2:
                if not self._open_safe_passage(maze, coordinate, random):
                    break

        while maze.cycle_count() < 2:
            candidates = list(maze.traversable_cells())
            random.shuffle(candidates)
            if not any(
                self._open_safe_passage(maze, coordinate, random)
                for coordinate in candidates
            ):
                raise GenerationError(
                    "Maze is too small to create two safe independent loops"
                )

        missing_corridors = {
            coordinate
            for coordinate in self._pacman_positions()
            if len(maze.passage_neighbors(coordinate)) < 2
        }
        if missing_corridors:
            raise GenerationError("Could not keep corners and centre open")
        if len(maze.dead_ends()) > 2:
            message = "Could not reduce dead ends to a rare amount"
            raise GenerationError(message)

    def _open_safe_passage(
        self,
        maze: Maze,
        coordinate: Coordinate,
        random: Random,
    ) -> bool:
        """Abra uma parede interna aleatória sem criar uma área 3x3."""
        candidates = self._closed_neighbor_walls(maze, coordinate)
        random.shuffle(candidates)
        for wall in candidates:
            maze.remove_wall(coordinate, wall)
            if maze.has_open_3x3_area():
                maze.add_wall(coordinate, wall)
                continue
            return True
        return False

    def _closed_neighbor_walls(
        self,
        maze: Maze,
        coordinate: Coordinate,
    ) -> list[Wall]:
        """Retorne paredes fechadas que levam a células transitáveis."""
        cell = maze.cell_at(coordinate)
        walls: list[Wall] = []
        for wall, delta_x, delta_y in DIRECTIONS:
            neighbor = Coordinate(
                coordinate.x + delta_x,
                coordinate.y + delta_y,
            )
            if (
                self._inside_grid(neighbor)
                and neighbor not in maze.pattern_cells
                and cell.has_wall(wall)
            ):
                walls.append(wall)
        return walls

    def _pacman_positions(self) -> set[Coordinate]:
        """Retorne os quatro cantos e o centro exigidos pelo modo."""
        return {
            Coordinate(0, 0),
            Coordinate(self.config.width - 1, 0),
            Coordinate(0, self.config.height - 1),
            Coordinate(self.config.width - 1, self.config.height - 1),
            Coordinate(self.config.width // 2, self.config.height // 2),
        }

    def _shortest_path(self, maze: Maze) -> list[Coordinate]:
        """Encontre o menor caminho usando busca em largura."""
        entry = self.config.entry
        exit_coordinate = self.config.exit
        queue = deque([entry])
        previous: dict[Coordinate, Coordinate | None] = {entry: None}

        while queue:
            current = queue.popleft()
            if current == exit_coordinate:
                break
            for neighbor in maze.passage_neighbors(current):
                if neighbor not in previous:
                    previous[neighbor] = current
                    queue.append(neighbor)

        if exit_coordinate not in previous:
            raise GenerationError("No path exists between entry and exit")

        path: list[Coordinate] = []
        path_cursor: Coordinate | None = exit_coordinate
        while path_cursor is not None:
            path.append(path_cursor)
            path_cursor = previous[path_cursor]
        path.reverse()
        return path

    def _validate_config(self) -> None:
        """Rejeite parâmetros que não descrevem um labirinto utilizável."""
        if self.config.width <= 0 or self.config.height <= 0:
            raise GenerationError("Maze dimensions must be positive")
        if not self._inside_grid(self.config.entry):
            raise GenerationError("Entry coordinate is outside the maze")
        if not self._inside_grid(self.config.exit):
            raise GenerationError("Exit coordinate is outside the maze")
        if self.config.entry == self.config.exit:
            raise GenerationError("Entry and exit must be different")

    def _inside_grid(self, coordinate: Coordinate) -> bool:
        """Informe se uma coordenada cabe nas dimensões configuradas."""
        return (
            0 <= coordinate.x < self.config.width
            and 0 <= coordinate.y < self.config.height
        )
