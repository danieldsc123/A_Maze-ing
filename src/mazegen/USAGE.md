# Reusing mazegen

Install the wheel with `python3 -m pip install mazegen-0.1.0-py3-none-any.whl`.
Requires Python 3.10 or newer; no third-party runtime dependencies.

```python
from pathlib import Path
from mazegen import Coordinate, MazeConfig, MazeGenerator

config = MazeConfig(
    width=20, height=15,
    entry=Coordinate(0, 0), exit=Coordinate(19, 14),
    output_file=Path("maze.txt"), perfect=True, seed=42,
)
maze = MazeGenerator(config).generate()
print(maze.cells[0][0].walls)
print(maze.solution)
print(maze.solution_directions())
```

Coordinates are zero-based `(x, y)`; access cells using `maze.cells[y][x]`.
Wall bits are N=1, E=2, S=4, W=8; a set bit means closed.
Use `maze.add_wall` / `maze.remove_wall` to keep shared walls consistent.
`pattern_cells` identifies closed cells forming the 42.
`solution` contains shortest-path coordinates, including both endpoints.
`solution_directions()` returns the equivalent N/E/S/W sequence.

Set `perfect=False` for a connected board with multiple loops and rare dead ends.
Keep parameters and seed fixed to reproduce a maze. Impossible configurations
raise `mazegen.errors.GenerationError`. Small grids can omit the 42 with a warning.
The generator does not read configuration files, write files or open a display.
`output_file` is used only by the CLI/export adapter.

MIT license: see the LICENSE.md included in the distribution.
