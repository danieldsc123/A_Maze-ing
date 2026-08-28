"""Interactive terminal rendering boundary."""

from mazegen.models import Maze


class TerminalRenderer:
    """Render a maze and coordinate terminal interactions."""

    def run(self, maze: Maze) -> None:
        """Start the interactive terminal view for a generated maze."""
        raise NotImplementedError("Terminal rendering is not implemented yet")
