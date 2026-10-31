from enum import Enum


class OperacaoLog(Enum):
    """Operações críticas registradas no log de auditoria (NF004)."""
    CADASTRO = "CADASTRO"
    EDICAO = "EDICAO"
    EXCLUSAO = "EXCLUSAO"
    VALIDACAO = "VALIDACAO"
