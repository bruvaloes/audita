from abc import ABC, abstractmethod

from entidade.usuario import Usuario


class ConsultaUsuarios(ABC):
    """Operações somente de leitura sobre usuários."""

    @abstractmethod
    def listar_todos(self) -> list[Usuario]:
        """Retorna todos os usuários, na ordem em que foram salvos."""

    @abstractmethod
    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        """Retorna o usuário com o CPF informado, ou None se não existir."""

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario | None:
        """Retorna o usuário com o e-mail informado, ou None se não existir."""


class PersistenciaUsuarios(ABC):
    """Operações de escrita sobre usuários."""

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        """Persiste o usuário, atribui um id único e o retorna."""


class UsuarioRepositorio(ConsultaUsuarios, PersistenciaUsuarios, ABC):
    """Contrato completo de repositório; qualquer mecanismo de persistência
    (memória, arquivo, banco) deve poder substituí-lo sem alterar o
    comportamento descrito acima."""
