*This project has been created as part of the 42 curriculum by danieldsc123, jandeson.*

# A-Maze-ing

## Description

A Python 3.10+ maze generator with perfect and Pac-Man-like modes, hexadecimal
wall output, shortest-path discovery and an interactive terminal view. This
initial `main` branch defines stable module boundaries so feature work can happen
in parallel with fewer merge conflicts.

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

The implementation is intentionally scaffold-only on this initial branch.
Feature branches will fill the generation, parser, serializer and renderer
boundaries before the first functional release.

## Configuration

The default `config.txt` uses one `KEY=VALUE` pair per line. Lines beginning
with `#` are comments. Mandatory keys are `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`,
`OUTPUT_FILE` and `PERFECT`; `SEED` is an additional reproducibility option.

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

