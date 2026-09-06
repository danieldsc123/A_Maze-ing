"""Testes das estruturas de dados do labirinto."""

from pathlib import Path

from mazegen.models import Cell, Coordinate, Maze, MazeConfig, Wall


def test_wall_values_use_independent_bits() -> None:
    """Represente cada parede com um bit independente."""
    assert Wall.NORTH == 1
    assert Wall.EAST == 2
    assert Wall.SOUTH == 4
    assert Wall.WEST == 8


def test_all_walls_form_hexadecimal_f() -> None:
    """Combine as quatro paredes no valor hexadecimal F."""
    walls = Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST

    assert int(walls) == 0xF


def test_cell_starts_without_walls() -> None:
    """Crie uma célula aberta por padrão."""
    cell = Cell()

    assert cell.walls == Wall(0)


def test_cell_can_add_and_check_a_wall() -> None:
    """Adicione uma parede sem afetar as outras direções."""
    cell = Cell()

    cell.add_wall(Wall.NORTH)

    assert cell.has_wall(Wall.NORTH)
    assert not cell.has_wall(Wall.SOUTH)


def test_cell_can_remove_a_wall() -> None:
    """Remova uma parede preservando as demais."""
    cell = Cell(Wall.NORTH | Wall.EAST)

    cell.remove_wall(Wall.NORTH)

    assert not cell.has_wall(Wall.NORTH)
    assert cell.has_wall(Wall.EAST)


def test_maze_stores_a_grid_of_cells() -> None:
    """Armazene células usando linhas e colunas."""
    config = MazeConfig(
        width=2,
        height=2,
        entry=Coordinate(0, 0),
        exit=Coordinate(1, 1),
        output_file=Path("maze.txt"),
    )
    cells = [
        [Cell(), Cell()],
        [Cell(), Cell()],
    ]

    maze = Maze(config=config, cells=cells)

    assert len(maze.cells) == 2
    assert len(maze.cells[0]) == 2
    assert isinstance(maze.cells[0][0], Cell)
    assert maze.solution == []


def test_fully_walled_maze_starts_with_hexadecimal_f() -> None:
    """Inicie todas as células com todas as paredes fechadas."""
    maze = Maze.fully_walled(_config())

    assert all(int(cell.walls) == 0xF for row in maze.cells for cell in row)
    assert maze.has_consistent_walls()


def test_remove_wall_updates_both_neighbouring_cells() -> None:
    """Mantenha paredes compartilhadas coerentes ao abrir uma passagem."""
    maze = Maze.fully_walled(_config())

    maze.remove_wall(Coordinate(0, 0), Wall.EAST)

    assert not maze.cell_at(Coordinate(0, 0)).has_wall(Wall.EAST)
    assert not maze.cell_at(Coordinate(1, 0)).has_wall(Wall.WEST)
    assert maze.has_consistent_walls()


def test_add_wall_updates_both_neighbouring_cells() -> None:
    """Mantenha paredes compartilhadas coerentes ao fechar uma passagem."""
    maze = Maze.fully_walled(_config())
    maze.remove_wall(Coordinate(0, 0), Wall.SOUTH)

    maze.add_wall(Coordinate(0, 0), Wall.SOUTH)

    assert maze.cell_at(Coordinate(0, 0)).has_wall(Wall.SOUTH)
    assert maze.cell_at(Coordinate(0, 1)).has_wall(Wall.NORTH)


def test_external_border_cannot_be_removed() -> None:
    """Mantenha o labirinto fechado em sua borda externa."""
    maze = Maze.fully_walled(_config())

    try:
        maze.remove_wall(Coordinate(0, 0), Wall.NORTH)
    except ValueError as error:
        assert "external border" in str(error)
    else:
        raise AssertionError("Expected external border removal to fail")


def test_consistency_check_detects_asymmetric_shared_wall() -> None:
    """Detecte paredes alteradas sem a API de mutação do labirinto."""
    maze = Maze.fully_walled(_config())

    maze.cell_at(Coordinate(0, 0)).remove_wall(Wall.EAST)

    assert not maze.has_consistent_walls()


def test_consistency_check_detects_open_external_border() -> None:
    """Detecte uma abertura inválida para fora do grid."""
    maze = Maze.fully_walled(_config())

    maze.cell_at(Coordinate(0, 0)).remove_wall(Wall.NORTH)

    assert not maze.has_consistent_walls()


def test_cell_at_rejects_coordinate_outside_grid() -> None:
    """Rejeite coordenadas negativas ou além dos limites."""
    maze = Maze.fully_walled(_config())

    for coordinate in (Coordinate(-1, 0), Coordinate(2, 1)):
        try:
            maze.cell_at(coordinate)
        except IndexError:
            pass
        else:
            raise AssertionError("Expected coordinate outside maze to fail")


def test_directional_operation_rejects_combined_wall_flags() -> None:
    """Exija uma direção ao alterar uma parede compartilhada."""
    maze = Maze.fully_walled(_config())

    try:
        maze.remove_wall(Coordinate(0, 0), Wall.EAST | Wall.SOUTH)
    except ValueError as error:
        assert "one cardinal wall" in str(error)
    else:
        raise AssertionError("Expected combined wall flags to fail")


def _config() -> MazeConfig:
    """Retorne uma configuração válida para os testes dos modelos."""
    return MazeConfig(
        width=2,
        height=2,
        entry=Coordinate(0, 0),
        exit=Coordinate(1, 1),
        output_file=Path("maze.txt"),
    )
