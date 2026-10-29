from abc import ABC, abstractmethod

from entidade.evidencia import Evidencia
from entidade.situacao_validacao import SituacaoValidacao


class ConsultaEvidencias(ABC):
    """Operações somente de leitura sobre evidências."""

    @abstractmethod
    def buscar_por_id(self, id_evidencia: int) -> Evidencia | None:
        """Retorna a evidência com o id informado, ou None se não existir."""

    @abstractmethod
    def listar(
        self,
        numero_contrato: str | None = None,
        id_funcionario: int | None = None,
    ) -> list[Evidencia]:
        """Retorna as evidências, na ordem em que foram salvas.

        Parâmetros opcionais filtram por contrato e/ou funcionário.
        """


class PersistenciaEvidencias(ABC):
    """Operações de escrita sobre evidências."""

    @abstractmethod
    def salvar(self, evidencia: Evidencia) -> Evidencia:
        """Persiste a evidência, atribui um id único e a retorna."""

    @abstractmethod
    def atualizar_situacao(
        self, id_evidencia: int, situacao: SituacaoValidacao
    ) -> None:
        """Atualiza apenas a situação de validação da evidência informada."""


class EvidenciaRepositorio(ConsultaEvidencias, PersistenciaEvidencias, ABC):
    """Contrato completo de repositório; qualquer mecanismo de persistência
    (memória, arquivo, banco) deve poder substituí-lo sem alterar o
    comportamento descrito acima."""
