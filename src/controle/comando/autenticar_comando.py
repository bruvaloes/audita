from dataclasses import dataclass

from controle.autenticacao_controller import AutenticacaoController
from controle.comando.comando import Comando
from entidade.usuario import Usuario


@dataclass(frozen=True)
class Credenciais:
    """Dados informados no login (RF 02)."""
    identificador: str
    senha: str
    perfil: str


class AutenticarComando(Comando[Usuario]):
    """Autentica o usuário pelo identificador, senha e perfil (RF 02)."""

    def __init__(self, autenticacao: AutenticacaoController,
                 credenciais: Credenciais):
        self._autenticacao = autenticacao
        self._credenciais = credenciais

    def executar(self) -> Usuario:
        return self._autenticacao.autenticar(
            identificador=self._credenciais.identificador,
            senha=self._credenciais.senha,
            perfil=self._credenciais.perfil,
        )
