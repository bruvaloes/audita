from typing import Mapping

from controle.acesso.operacao import Operacao
from controle.acesso.permissoes import PERMISSOES_PADRAO
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.acesso_negado_error import AcessoNegadoError


class ControleAcesso:
    """Decide se um usuário pode executar uma operação, pelo perfil dele.

    Sem usuário autenticado (None), nenhuma operação é permitida.
    """

    def __init__(self, permissoes: Mapping[Perfil, frozenset[Operacao]]
                 = PERMISSOES_PADRAO):
        self._permissoes = permissoes

    def permite(self, usuario: Usuario | None, operacao: Operacao) -> bool:
        if usuario is None:
            return False
        return operacao in self._permissoes.get(usuario.perfil, frozenset())

    def verificar(self, usuario: Usuario | None, operacao: Operacao) -> None:
        """Levanta AcessoNegadoError quando o usuário não pode executar."""
        if not self.permite(usuario, operacao):
            raise AcessoNegadoError()
