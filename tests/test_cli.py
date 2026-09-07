"""Testes do contrato estável da linha de comando."""

from pathlib import Path
from unittest.mock import patch

from mazegen.cli import main


def test_cli_requires_exactly_one_argument() -> None:
    """Rejeite a execução sem um caminho de configuração."""
    assert main([]) == 2


def test_full_cli(tmp_path: Path) -> None:
    """Execute a aplicação completa e valide o arquivo produzido."""
    config = tmp_path / "config.txt"
    output = tmp_path / "maze.txt"
    config.write_text(
        "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
        f"OUTPUT_FILE={output}\nPERFECT=False\nSEED=42\n")
    with patch("sys.stdin.isatty", return_value=False):
        assert main([str(config)]) == 0
    assert len(output.read_text().splitlines()) == 19
