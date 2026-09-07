*This project has been created as part of the 42 curriculum by danda-si, jandeson*

# A-Maze-ing

## Description

A Python 3.10+ maze generator with perfect and Pac-Man-like modes, hexadecimal
wall output, shortest-path discovery and an interactive terminal view. The generator, configuration parser, hexadecimal exporter and interactive
terminal renderer use separate modules.

## Architecture

```text
a_maze_ing.py              CLI entry point required by the subject
src/mazegen/
  models.py                shared typed data contracts
  generator.py             MazeGenerator and core generation algorithms
  config.py                KEY=VALUE parsing and validation
  serializer.py            hexadecimal output format
  renderer.py              terminal display and interactions
  cli.py                   application orchestration and user-facing errors
tests/                     development tests (remove before final submission)
```

Dependency direction: `cli` composes the modules; adapters (`config`,
`serializer`, `renderer`) depend on shared models; the generator depends only on
models and domain errors. The reusable package never imports the root script.

## Instructions

Create a virtual environment, then run:

```sh
make install
make lint
make test
make run
```

In an interactive terminal, type a command and press Enter:

- `r`: generate another maze and update the output file.
- `s`: show/hide the shortest path.
- `c`: cycle wall colors.
- `q`: exit (EOF and Ctrl-C also close the interface).

`E` marks entry, `X` exit, `#` the 42 pattern and `*` the visible solution.
When stdin or stdout is redirected, the application prints one plain ASCII
image and exits without requesting input. Regeneration uses a fresh seed;
the initial generation still uses the configured seed.

## Configuration

The default `config.txt` uses one `KEY=VALUE` pair per line. Lines beginning
with `#` are comments. Mandatory keys are `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`,
`OUTPUT_FILE` and `PERFECT`; `SEED` is an optional integer reproducibility option. Dimensions must be positive,
coordinates are zero-based `x,y`, and entry/exit must differ and lie inside the
grid. `PERFECT` accepts `True` or `False`. Blank lines and comment lines are
ignored; unknown/duplicate keys, empty values and malformed lines are rejected.
Relative `OUTPUT_FILE` paths are resolved from the working directory.

The UTF-8 output contains one uppercase hexadecimal digit per cell, followed
by a blank line, entry coordinates, exit coordinates and the shortest path as
`N/E/S/W`. Every line, including the last, ends with LF.

Generation uses iterative randomized DFS: it visits each traversable cell once,
creating a connected maze without cycles in perfect mode. Non-perfect mode
opens additional safe passages to add cycles and reduce dead ends. A BFS finds
the shortest path because every passage has the same cost. The 42 consists of
reserved closed cells; small grids emit a warning and omit it.

## Reusable package

After installation, the generator can be used without the CLI:

```python
from pathlib import Path
from mazegen import Coordinate, MazeConfig, MazeGenerator

config = MazeConfig(20, 15, Coordinate(0, 0), Coordinate(19, 14),
                    Path("maze.txt"), perfect=True, seed=42)
maze = MazeGenerator(config).generate()
print(maze.solution_directions())
```

`maze.cells[y][x].walls` exposes the wall bits; `maze.solution` contains the
solution coordinates. `make build` creates distributions under `dist/`.

Implementation was checked against the requirements recorded in Trello.
Comparison with the original Subject v2.3 PDF and validation with its supplied
`maze_analyzer.py` remain pending.

## Team and project management

- Daniel: maze data structure, walls, `MazeGenerator`, seeded algorithms,
  perfect/non-perfect modes, the 42 pattern, connectivity and shortest path.
- Janderson: configuration, environment/Makefile, hexadecimal output and
  terminal visualization/interactions.
- Both: integration, reusable package, license, documentation, tests,
  `maze_analyzer.py` validation and peer-evaluation preparation.

Work follows the Trello flow Backlog -> To Do -> In Progress -> Review -> Done.
The author implements a card; the other teammate reviews it and must be able to
explain the result.

## Resources

- Python documentation: https://docs.python.org/3/
- Python packaging guide: https://packaging.python.org/
- mypy documentation: https://mypy.readthedocs.io/
- flake8 documentation: https://flake8.pycqa.org/

AI was used to compare the subject with the Trello plan and to scaffold the
initial architecture. Every generated change must be reviewed, tested and
understood by both teammates before evaluation.

