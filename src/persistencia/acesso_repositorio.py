from abc import ABC, abstractmethod

from entidade.acesso import Acesso


class ConsultaAcessos(ABC):
    """Operações somente de leitura sobre acessos."""

    @abstractmethod
    def listar_todos(self) -> list[Acesso]:
        """Retorna todos os acessos, na ordem em que foram salvos."""


class PersistenciaAcessos(ABC):
    """Operações de escrita sobre acessos."""

    @abstractmethod
    def salvar(self, acesso: Acesso) -> Acesso:
        """Persiste o acesso, atribui um id único e o retorna."""


class AcessoRepositorio(ConsultaAcessos, PersistenciaAcessos, ABC):
    """Contrato completo de repositório de acessos; qualquer mecanismo de
    persistência deve poder substituí-lo sem alterar o comportamento descrito
    acima."""
