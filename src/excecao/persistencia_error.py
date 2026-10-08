class PersistenciaError(Exception):
    """Base para todos os erros do mecanismo de armazenamento de dados."""


class ConexaoPersistenciaError(PersistenciaError):
    """Falha ao abrir ou preparar o armazenamento."""


class LeituraPersistenciaError(PersistenciaError):
    """Falha ao consultar dados no armazenamento."""


class EscritaPersistenciaError(PersistenciaError):
    """Falha ao gravar dados no armazenamento."""
