from abc import ABC, abstractmethod


class HashSenha(ABC):
    """Transforma a senha em um hash irreversível e confere senhas contra ele."""

    @abstractmethod
    def gerar(self, senha: str) -> str:
        """Retorna o hash da senha, com salt próprio para cada chamada."""

    @abstractmethod
    def verificar(self, senha: str, hash_senha: str) -> bool:
        """Indica se a senha corresponde ao hash (False se o hash for inválido)."""
