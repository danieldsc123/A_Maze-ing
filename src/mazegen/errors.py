"""Exceções específicas do domínio expostas pelo pacote."""


class MazeError(Exception):
    """Exceção-base para erros que podem ser exibidos ao usuário."""


class ConfigurationError(MazeError):
    """Indique que um arquivo ou valor de configuração é inválido."""


class GenerationError(MazeError):
    """Indique que o labirinto não pode ser gerado com os parâmetros."""
