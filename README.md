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
The solution forms a continuous trail through open passages. Entry, exit,
pattern and solution have distinct colors in an interactive terminal.
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

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

The UTF-8 output contains one uppercase hexadecimal digit per cell, followed
by a blank line, entry coordinates, exit coordinates and the shortest path as
`N/E/S/W`. Every line, including the last, ends with LF.

DFS was chosen for its simple stack-based implementation, linear traversal
and direct construction of a spanning tree. The explicit stack avoids Python
recursion limits on long corridors.

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
solution coordinates. `make build` creates `mazegen-0.1.0-py3-none-any.whl`
at the repository root. The wheel contains `mazegen/USAGE.md` and the license.

The original Subject v2.3 was checked on 2026-09-07. Chapter V explicitly
allows terminal ASCII rendering as an alternative to MLX. The supplied
`maze_analyzer.py` reports PERFECT for the 20x15, seed 42 perfect output and
Pac-Man-USABLE for the non-perfect output (27 loops, zero real dead ends).
An independent BFS over the exported hexadecimal grid also confirmed shortest
solutions of 149 and 43 steps respectively, closed borders and LF line endings.
These checks cover those configurations, not every possible input.

Rebuild the wheel with `make build`. Install it in another virtual environment
with `python3 -m pip install /absolute/path/to/mazegen-0.1.0-py3-none-any.whl`.
Build isolation requires setuptools >=77, which supports the license metadata
used here. If the campus package mirror cannot supply dependencies, use
`PIP_INDEX_URL=https://pypi.org/simple make install` (or `make build`).
The lint configuration excludes virtual environments and build artifacts.
Development tests are kept during development; prepare the final submission
without those test programs as requested in chapter III.3.

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

The original plan separated Daniel's core generation from Janderson's
configuration and interface through shared data contracts. In the work recorded
so far, the core was integrated first; Daniel then requested implementation of
the remaining parser, output and interface with AI assistance. Those changes
were published as dependent branches: `feat/config-parser` -> `feat/hex-output`
-> `feat/terminal-interface`. Peer review and final integration remain pending.

The stable `MazeConfig`/`Maze` contracts allowed the adapters to be implemented
without changing the core. An improvement for the remaining work is to check
the original subject and analyzer earlier and keep Trello, README and Git
status synchronized. Tools used include Git/GitHub, Trello, pytest, flake8,
mypy, virtual environments and the supplied analyzer. The team should add its
own final retrospective after review and delivery.

## Resources

- Python documentation: https://docs.python.org/3/
- Python packaging guide: https://packaging.python.org/
- mypy documentation: https://mypy.readthedocs.io/
- flake8 documentation: https://flake8.pycqa.org/

AI assisted the initial architecture and requirements comparison, and later
implemented the configuration parser, hexadecimal serializer, terminal renderer,
CLI regeneration integration and their tests at Daniel's request. It also
updated documentation, organized branches/Trello and ran validation commands. Every generated change must be reviewed, tested and
understood by both teammates before evaluation.

