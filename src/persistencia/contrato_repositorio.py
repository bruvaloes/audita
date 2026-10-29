from abc import ABC, abstractmethod

from entidade.contrato import Contrato


class ConsultaContratos(ABC):
    """Operações somente de leitura sobre contratos."""

    @abstractmethod
    def buscar_por_numero(self, numero: str) -> Contrato | None:
        """Retorna o contrato com o número informado, ou None se não existir."""

    @abstractmethod
    def listar(self) -> list[Contrato]:
        """Retorna todos os contratos, na ordem em que foram salvos."""


class PersistenciaContratos(ABC):
    """Operações de escrita sobre contratos."""

    @abstractmethod
    def salvar(self, contrato: Contrato) -> Contrato:
        """Persiste o contrato, atribui um id único e o retorna."""

    @abstractmethod
    def atualizar(self, contrato: Contrato) -> None:
        """Sobrescreve os dados do contrato já existente (identificado pelo número)."""

    @abstractmethod
    def remover(self, numero: str) -> None:
        """Remove o contrato com o número informado. Não faz nada se não existir."""


class ContratoRepositorio(ConsultaContratos, PersistenciaContratos, ABC):
    """Contrato completo de repositório; qualquer mecanismo de persistência
    (memória, arquivo, banco) deve poder substituí-lo sem alterar o
    comportamento descrito acima."""
