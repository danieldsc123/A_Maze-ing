"""Leitura e validação de configurações KEY=VALUE."""

from pathlib import Path

from mazegen.errors import ConfigurationError
from mazegen.models import Coordinate, MazeConfig


REQUIRED = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


def load_config(path: Path) -> MazeConfig:
    """Leia UTF-8 e rejeite sintaxe, chaves e valores inválidos."""
    try:
        with path.open(encoding="utf-8") as source:
            lines = source.readlines()
    except (OSError, UnicodeError) as error:
        message = f"Cannot read configuration: {error}"
        raise ConfigurationError(message) from error
    values: dict[str, str] = {}
    for number, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not separator or not value:
            raise ConfigurationError(f"Line {number}: expected KEY=VALUE")
        if key not in REQUIRED | {"SEED"}:
            raise ConfigurationError(f"Line {number}: unknown key {key}")
        if key in values:
            raise ConfigurationError(f"Line {number}: duplicate key {key}")
        values[key] = value
    missing = REQUIRED - values.keys()
    if missing:
        raise ConfigurationError(f"Missing keys: {', '.join(sorted(missing))}")
    try:
        width, height = int(values["WIDTH"]), int(values["HEIGHT"])
        entry = _coordinate(values["ENTRY"])
        exit_cell = _coordinate(values["EXIT"])
        seed = int(values["SEED"]) if "SEED" in values else None
    except ValueError as error:
        message = f"Invalid integer or coordinate: {error}"
        raise ConfigurationError(message) from error
    if width <= 0 or height <= 0:
        raise ConfigurationError("WIDTH and HEIGHT must be positive")
    for name, coordinate in (("ENTRY", entry), ("EXIT", exit_cell)):
        if not (0 <= coordinate.x < width and 0 <= coordinate.y < height):
            raise ConfigurationError(f"{name} is outside the maze")
    if entry == exit_cell:
        raise ConfigurationError("ENTRY and EXIT must be different")
    if values["PERFECT"] not in {"True", "False"}:
        raise ConfigurationError("PERFECT must be True or False")
    if "\x00" in values["OUTPUT_FILE"]:
        raise ConfigurationError("OUTPUT_FILE contains a null character")
    return MazeConfig(width, height, entry, exit_cell,
                      Path(values["OUTPUT_FILE"]),
                      values["PERFECT"] == "True", seed)


def _coordinate(value: str) -> Coordinate:
    """Converta um par x,y em coordenada."""
    x, y = value.split(",")
    return Coordinate(int(x), int(y))
