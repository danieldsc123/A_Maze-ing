"""Fronteira de leitura e validação da configuração."""

from pathlib import Path

from mazegen.errors import ConfigurationError
from mazegen.models import MazeConfig


def load_config(path: Path) -> MazeConfig:
    """Carregue e valide um arquivo de configuração KEY=VALUE.

    O parser completo pertence à sua branch de funcionalidade dedicada.
    """
    if not path.is_file():
        raise ConfigurationError(f"Configuration file not found: {path}")
    raise ConfigurationError("Configuration parsing is not implemented yet")
