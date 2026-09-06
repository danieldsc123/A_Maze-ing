"""Fronteira da renderização interativa no terminal."""

from mazegen.models import Maze


class TerminalRenderer:
    """Renderize um labirinto e coordene as interações do terminal."""

    def run(self, maze: Maze) -> None:
        """Inicie a visualização interativa do labirinto no terminal."""
        raise NotImplementedError("Terminal rendering is not implemented yet")
