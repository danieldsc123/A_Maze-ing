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
