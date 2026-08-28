"""Tests for the stable command-line contract."""

from mazegen.cli import main


def test_cli_requires_exactly_one_argument() -> None:
    """Reject invocation without a configuration path."""
    assert main([]) == 2
