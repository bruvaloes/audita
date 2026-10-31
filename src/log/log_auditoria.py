from abc import ABC, abstractmethod

from log.registro_log import RegistroLog


class LogAuditoria(ABC):
    """Interface própria do sistema para registro de auditoria (Target do Adapter).

    O restante da aplicação conhece apenas esta interface.
    Operações permitidas: somente acrescentar (registrar) e consultar (listar).
    A aplicação não tem nenhuma operação para alterar ou apagar registros (NF004).
    """

    @abstractmethod
    def registrar(self, registro: RegistroLog) -> None:
        """Registra uma ação crítica no log de auditoria."""

    @abstractmethod
    def listar(self) -> list[RegistroLog]:
        """Retorna todos os registros de auditoria em ordem cronológica."""
