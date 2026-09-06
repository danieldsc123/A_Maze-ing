"""Testes do contrato estável da linha de comando."""

from mazegen.cli import main


def test_cli_requires_exactly_one_argument() -> None:
    """Rejeite a execução sem um caminho de configuração."""
    assert main([]) == 2
