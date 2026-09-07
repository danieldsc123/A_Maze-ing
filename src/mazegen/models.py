"""Contratos de dados compartilhados e sem dependências da aplicação."""

from dataclasses import dataclass, field
from enum import IntFlag
from pathlib import Path


class Wall(IntFlag):
    """Representa paredes usando os quatro bits de menor ordem."""

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
    """Representa uma célula do labirinto e suas paredes."""

    walls: Wall = Wall(0)

    def add_wall(self, wall: Wall) -> None:
        """Adiciona uma ou mais paredes à célula."""
        self.walls |= wall

    def remove_wall(self, wall: Wall) -> None:
        """Remove uma ou mais paredes da célula."""
        self.walls &= ~wall

    def has_wall(self, wall: Wall) -> bool:
        """Informa se a célula contém todas as paredes solicitadas."""
        return (self.walls & wall) == wall


@dataclass(frozen=True)
class Coordinate:
    """Representa uma coordenada de célula iniciada em zero."""

    x: int
    y: int


@dataclass(frozen=True)
class MazeConfig:
    """Armazena as opções validadas necessárias para gerar o labirinto."""

    width: int
    height: int
    entry: Coordinate
    exit: Coordinate
    output_file: Path
    perfect: bool = False
    seed: int | None = None


@dataclass
class Maze:
    """Expoe as paredes geradas e um caminho de solução mais curto."""

    config: MazeConfig
    cells: list[list[Cell]]
    solution: list[Coordinate] = field(default_factory=list)
    pattern_cells: set[Coordinate] = field(default_factory=set)

    @classmethod
    def fully_walled(cls, config: MazeConfig) -> "Maze":
        """Cria um grid cujas células começam com as quatro paredes."""
        all_walls = Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST
        cells = [
            [Cell(all_walls) for _ in range(config.width)]
            for _ in range(config.height)
        ]
        return cls(config=config, cells=cells)

    def contains(self, coordinate: Coordinate) -> bool:
        """Informa se uma coordenada está dentro do grid."""
        return (
            0 <= coordinate.x < self.config.width
            and 0 <= coordinate.y < self.config.height
        )

    def cell_at(self, coordinate: Coordinate) -> Cell:
        """Retorna a célula localizada em uma coordenada válida.

        Levanta:
            IndexError: Quando a coordenada está fora do labirinto.
        """
        if not self.contains(coordinate):
            raise IndexError(f"Coordinate outside maze: {coordinate}")
        return self.cells[coordinate.y][coordinate.x]

    def add_wall(self, coordinate: Coordinate, wall: Wall) -> None:
        """Adiciona uma parede à célula e à vizinha, quando existir."""
        self._require_cardinal_wall(wall)
        self.cell_at(coordinate).add_wall(wall)
        neighbour = self._neighbour(coordinate, wall)
        if neighbour is not None:
            self.cell_at(neighbour).add_wall(OPPOSITE_WALL[wall])

    def remove_wall(self, coordinate: Coordinate, wall: Wall) -> None:
        """Remove uma parede compartilhada sem abrir a borda externa.

        Levanta:
            ValueError: Quando a parede solicitada aponta para fora do grid.
        """
        self._require_cardinal_wall(wall)
        neighbour = self._neighbour(coordinate, wall)
        if neighbour is None:
            raise ValueError("Cannot remove a wall from the external border")
        self.cell_at(coordinate).remove_wall(wall)
        self.cell_at(neighbour).remove_wall(OPPOSITE_WALL[wall])

    def has_consistent_walls(self) -> bool:
        """Verifica as bordas externas e paredes compartilhadas."""
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
        """Retorna células alcançáveis através de paredes abertas."""
        cell = self.cell_at(coordinate)
        neighbors: list[Coordinate] = []
        for wall in CARDINAL_WALLS:
            neighbor = self._neighbour(coordinate, wall)
            if neighbor is not None and not cell.has_wall(wall):
                neighbors.append(neighbor)
        return neighbors

    def solution_directions(self) -> str:
        """Codifica a solução como uma sequência de N, E, S e W."""
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
        """Conta passagens uma vez, inspecionando apenas leste e sul."""
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
        """Retorna as células não reservadas para o padrão 42."""
        return {
            Coordinate(x, y)
            for y in range(self.config.height)
            for x in range(self.config.width)
            if Coordinate(x, y) not in self.pattern_cells
        }

    def dead_ends(self) -> set[Coordinate]:
        """Retorna células transitáveis com exatamente uma passagem."""
        return {
            coordinate
            for coordinate in self.traversable_cells()
            if len(self.passage_neighbors(coordinate)) == 1
        }

    def cycle_count(self) -> int:
        """Retorna a quantidade de ciclos independentes do labirinto."""
        vertices = len(self.traversable_cells())
        return self.open_edge_count() - vertices + 1

    def has_open_3x3_area(self) -> bool:
        """Informa se algum grupo 3x3 não possui paredes internas."""
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
        """Retorna a vizinha após uma parede, se estiver dentro do grid."""
        delta_x, delta_y = WALL_DELTAS[wall]
        neighbour = Coordinate(
            coordinate.x + delta_x,
            coordinate.y + delta_y,
        )
        return neighbour if self.contains(neighbour) else None

    @staticmethod
    def _require_cardinal_wall(wall: Wall) -> None:
        """Rejeita paredes vazias ou combinadas em operações direcionais."""
        if wall not in CARDINAL_WALLS:
            raise ValueError(f"Expected one cardinal wall, received: {wall!r}")
