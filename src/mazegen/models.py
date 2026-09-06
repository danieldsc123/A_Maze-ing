"""Shared, dependency-free data contracts for the application."""

from dataclasses import dataclass, field
from enum import IntFlag
from pathlib import Path


class Wall(IntFlag):
    """Represent cell walls using the four low-order bits."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8


CARDINAL_WALLS = (Wall.NORTH, Wall.EAST, Wall.SOUTH, Wall.WEST)
WALL_DELTAS = {
    Wall.NORTH: (0, -1),
    Wall.EAST: (1, 0),
    Wall.SOUTH: (0, 1),
    Wall.WEST: (-1, 0),
}
OPPOSITE_WALL = {
    Wall.NORTH: Wall.SOUTH,
    Wall.EAST: Wall.WEST,
    Wall.SOUTH: Wall.NORTH,
    Wall.WEST: Wall.EAST,
}


@dataclass
class Cell:
    """Represent one maze cell and its surrounding walls."""

    walls: Wall = Wall(0)

    def add_wall(self, wall: Wall) -> None:
        """Add one or more walls to the cell."""
        self.walls |= wall

    def remove_wall(self, wall: Wall) -> None:
        """Remove one or more walls from the cell."""
        self.walls &= ~wall

    def has_wall(self, wall: Wall) -> bool:
        """Return whether the cell contains all requested walls."""
        return (self.walls & wall) == wall


@dataclass(frozen=True)
class Coordinate:
    """Represent a zero-based cell coordinate."""

    x: int
    y: int


@dataclass(frozen=True)
class MazeConfig:
    """Contain validated options required to generate a maze."""

    width: int
    height: int
    entry: Coordinate
    exit: Coordinate
    output_file: Path
    perfect: bool = False
    seed: int | None = None


@dataclass
class Maze:
    """Expose generated wall data and a shortest solution path."""

    config: MazeConfig
    cells: list[list[Cell]]
    solution: list[Coordinate] = field(default_factory=list)

    @classmethod
    def fully_walled(cls, config: MazeConfig) -> "Maze":
        """Create a grid whose cells initially contain all four walls."""
        all_walls = Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST
        cells = [
            [Cell(all_walls) for _ in range(config.width)]
            for _ in range(config.height)
        ]
        return cls(config=config, cells=cells)

    def contains(self, coordinate: Coordinate) -> bool:
        """Return whether a coordinate is inside the grid."""
        return (
            0 <= coordinate.x < self.config.width
            and 0 <= coordinate.y < self.config.height
        )

    def cell_at(self, coordinate: Coordinate) -> Cell:
        """Return the cell at a valid coordinate.

        Raises:
            IndexError: If the coordinate is outside the maze.
        """
        if not self.contains(coordinate):
            raise IndexError(f"Coordinate outside maze: {coordinate}")
        return self.cells[coordinate.y][coordinate.x]

    def add_wall(self, coordinate: Coordinate, wall: Wall) -> None:
        """Add a wall to a cell and its neighbour when one exists."""
        self._require_cardinal_wall(wall)
        self.cell_at(coordinate).add_wall(wall)
        neighbour = self._neighbour(coordinate, wall)
        if neighbour is not None:
            self.cell_at(neighbour).add_wall(OPPOSITE_WALL[wall])

    def remove_wall(self, coordinate: Coordinate, wall: Wall) -> None:
        """Remove a shared wall without opening the external border.

        Raises:
            ValueError: If the requested wall faces outside the grid.
        """
        self._require_cardinal_wall(wall)
        neighbour = self._neighbour(coordinate, wall)
        if neighbour is None:
            raise ValueError("Cannot remove a wall from the external border")
        self.cell_at(coordinate).remove_wall(wall)
        self.cell_at(neighbour).remove_wall(OPPOSITE_WALL[wall])

    def has_consistent_walls(self) -> bool:
        """Check external borders and every wall shared by two cells."""
        for y in range(self.config.height):
            for x in range(self.config.width):
                coordinate = Coordinate(x, y)
                cell = self.cell_at(coordinate)
                for wall in CARDINAL_WALLS:
                    neighbour = self._neighbour(coordinate, wall)
                    if neighbour is None:
                        if not cell.has_wall(wall):
                            return False
                        continue
                    neighbour_has_wall = self.cell_at(neighbour).has_wall(
                        OPPOSITE_WALL[wall]
                    )
                    if cell.has_wall(wall) != neighbour_has_wall:
                        return False
        return True

    def _neighbour(
        self,
        coordinate: Coordinate,
        wall: Wall,
    ) -> Coordinate | None:
        """Return the neighbour across a wall, if it is inside the grid."""
        delta_x, delta_y = WALL_DELTAS[wall]
        neighbour = Coordinate(
            coordinate.x + delta_x,
            coordinate.y + delta_y,
        )
        return neighbour if self.contains(neighbour) else None

    @staticmethod
    def _require_cardinal_wall(wall: Wall) -> None:
        """Reject empty or combined wall flags for directional operations."""
        if wall not in CARDINAL_WALLS:
            raise ValueError(f"Expected one cardinal wall, received: {wall!r}")
