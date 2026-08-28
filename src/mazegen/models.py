"""Shared, dependency-free data contracts for the application."""

from dataclasses import dataclass, field
from pathlib import Path


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
    cells: list[list[int]]
    solution: list[Coordinate] = field(default_factory=list)
