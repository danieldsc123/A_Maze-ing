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
    pattern_cells: set[Coordinate] = field(default_factory=set)

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

    def passage_neighbors(self, coordinate: Coordinate) -> list[Coordinate]:
        """Return cells reachable from a coordinate through open walls."""
        cell = self.cell_at(coordinate)
        neighbors: list[Coordinate] = []
        for wall in CARDINAL_WALLS:
            neighbor = self._neighbour(coordinate, wall)
            if neighbor is not None and not cell.has_wall(wall):
                neighbors.append(neighbor)
        return neighbors

    def solution_directions(self) -> str:
        """Encode the stored solution as a sequence of N, E, S and W."""
        directions: list[str] = []
        symbols = {
            (0, -1): "N",
            (1, 0): "E",
            (0, 1): "S",
            (-1, 0): "W",
        }
        for current, following in zip(self.solution, self.solution[1:]):
            delta = (following.x - current.x, following.y - current.y)
            try:
                directions.append(symbols[delta])
            except KeyError as error:
                message = "Solution contains non-adjacent cells"
                raise ValueError(message) from error
        return "".join(directions)

    def open_edge_count(self) -> int:
        """Count passages once by inspecting only east and south walls."""
        count = 0
        for y in range(self.config.height):
            for x in range(self.config.width):
                coordinate = Coordinate(x, y)
                cell = self.cell_at(coordinate)
                east_inside = x + 1 < self.config.width
                if east_inside and not cell.has_wall(Wall.EAST):
                    count += 1
                south_inside = y + 1 < self.config.height
                if south_inside and not cell.has_wall(Wall.SOUTH):
                    count += 1
        return count

    def traversable_cells(self) -> set[Coordinate]:
        """Return every cell that is not reserved for the closed 42 pattern."""
        return {
            Coordinate(x, y)
            for y in range(self.config.height)
            for x in range(self.config.width)
            if Coordinate(x, y) not in self.pattern_cells
        }

    def dead_ends(self) -> set[Coordinate]:
        """Return traversable cells with exactly one available passage."""
        return {
            coordinate
            for coordinate in self.traversable_cells()
            if len(self.passage_neighbors(coordinate)) == 1
        }

    def cycle_count(self) -> int:
        """Return the independent-cycle count for a connected maze."""
        vertices = len(self.traversable_cells())
        return self.open_edge_count() - vertices + 1

    def has_open_3x3_area(self) -> bool:
        """Return whether any 3x3 group has no internal walls."""
        for top in range(self.config.height - 2):
            for left in range(self.config.width - 2):
                area = {
                    Coordinate(x, y)
                    for y in range(top, top + 3)
                    for x in range(left, left + 3)
                }
                if area & self.pattern_cells:
                    continue
                horizontal_open = all(
                    not self.cell_at(Coordinate(x, y)).has_wall(Wall.EAST)
                    for y in range(top, top + 3)
                    for x in range(left, left + 2)
                )
                vertical_open = all(
                    not self.cell_at(Coordinate(x, y)).has_wall(Wall.SOUTH)
                    for y in range(top, top + 2)
                    for x in range(left, left + 3)
                )
                if horizontal_open and vertical_open:
                    return True
        return False

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
