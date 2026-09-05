"""Reusable maze-generation boundary owned by the core domain."""

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
        """Create and return the initial fully walled maze."""
        return Maze.fully_walled(self.config)

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
