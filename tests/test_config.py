"""Validação de configurações reais e erros de entrada."""
from pathlib import Path

import pytest

from mazegen.config import load_config
from mazegen.errors import ConfigurationError


VALID = ("# example\n\nWIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
         "OUTPUT_FILE=maze.txt\nPERFECT=False\nSEED=42\n")


def test_read_config(tmp_path: Path) -> None:
    """Leia comentários, coordenadas e parâmetros opcionais."""
    path = tmp_path / "config.txt"
    path.write_text(VALID, encoding="utf-8")
    config = load_config(path)
    assert (config.width, config.height, config.seed) == (20, 15, 42)
    assert not config.perfect
    path.write_text(VALID.replace("SEED=42\n", ""), encoding="utf-8")
    assert load_config(path).seed is None


@pytest.mark.parametrize("content", [
    VALID.replace("WIDTH=20", "WIDTH=0"),
    VALID.replace("ENTRY=0,0", "ENTRY=20,0"),
    VALID.replace("EXIT=19,14", "EXIT=0,0"),
    VALID.replace("ENTRY=0,0", "ENTRY=0,0,0"),
    VALID.replace("PERFECT=False", "PERFECT=yes"),
    VALID.replace("SEED=42", "SEED=x"),
    VALID.replace("WIDTH=20\n", ""),
    VALID + "WIDTH=4\n", VALID + "UNKNOWN=1\n",
    VALID + "broken\n", VALID.replace("OUTPUT_FILE=maze.txt", "OUTPUT_FILE="),
])
def test_invalid_config(tmp_path: Path, content: str) -> None:
    """Rejeite configurações inválidas com erro do domínio."""
    path = tmp_path / "config.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(path)


def test_unreadable_config(tmp_path: Path) -> None:
    """Trate arquivo ausente e codificação inválida."""
    path = tmp_path / "missing"
    with pytest.raises(ConfigurationError):
        load_config(path)
    path.write_bytes(b"\xff")
    with pytest.raises(ConfigurationError):
        load_config(path)
