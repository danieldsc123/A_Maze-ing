"""Reusable maze-generation boundary owned by the core domain."""

from collections import deque
from random import Random

from mazegen.errors import GenerationError
from mazegen.models import Coordinate, Maze, MazeConfig, Wall


DIRECTIONS: tuple[tuple[Wall, int, int], ...] = (
    (Wall.NORTH, 0, -1),
    (Wall.EAST, 1, 0),
    (Wall.SOUTH, 0, 1),
    (Wall.WEST, -1, 0),
)


class MazeGenerator:
    """Generate mazes from validated configuration.

    The generation algorithms will be implemented on their dedicated feature
    branches. Keeping this public contract stable lets the CLI, renderer and
    serializer evolve independently.
    """

    def __init__(self, config: MazeConfig) -> None:
        """Store the validated generation configuration."""
        self.config = config

    def generate(self) -> Maze:
        """Generate a connected perfect maze and its shortest solution."""
        self._validate_config()
        maze = Maze.fully_walled(self.config)
        random = Random(self.config.seed)
        visited = {self.config.entry}
        stack = [self.config.entry]

        while stack:
            current = stack[-1]
            neighbors = self._unvisited_neighbors(current, visited)
            if not neighbors:
                stack.pop()
                continue

            neighbor, wall = random.choice(neighbors)
            maze.remove_wall(current, wall)
            visited.add(neighbor)
            stack.append(neighbor)

        expected_cells = self.config.width * self.config.height
        if len(visited) != expected_cells:
            raise GenerationError("Could not connect every maze cell")

        maze.solution = self._shortest_path(maze)
        return maze

    def _unvisited_neighbors(
        self,
        coordinate: Coordinate,
        visited: set[Coordinate],
    ) -> list[tuple[Coordinate, Wall]]:
        """Return valid neighbouring cells that were not visited."""
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

            if inside_grid and neighbor not in visited:
                neighbors.append((neighbor, wall))

        return neighbors

    def _shortest_path(self, maze: Maze) -> list[Coordinate]:
        """Find a shortest entry-to-exit path using breadth-first search."""
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
        """Reject parameters that cannot describe a usable maze."""
        if self.config.width <= 0 or self.config.height <= 0:
            raise GenerationError("Maze dimensions must be positive")
        if not self._inside_grid(self.config.entry):
            raise GenerationError("Entry coordinate is outside the maze")
        if not self._inside_grid(self.config.exit):
            raise GenerationError("Exit coordinate is outside the maze")
        if self.config.entry == self.config.exit:
            raise GenerationError("Entry and exit must be different")

    def _inside_grid(self, coordinate: Coordinate) -> bool:
        """Return whether a coordinate fits the configured dimensions."""
        return (
            0 <= coordinate.x < self.config.width
            and 0 <= coordinate.y < self.config.height
        )
