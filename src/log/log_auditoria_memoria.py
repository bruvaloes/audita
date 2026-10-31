from log.log_auditoria import LogAuditoria
from log.registro_log import RegistroLog


class LogAuditoriaMemoria(LogAuditoria):
    """Implementação em memória de LogAuditoria para testes e persistência volátil (NF001)."""

    def __init__(self) -> None:
        self._registros: list[RegistroLog] = []

    def registrar(self, registro: RegistroLog) -> None:
        self._registros.append(registro)

    def listar(self) -> list[RegistroLog]:
        return list(self._registros)
