from dataclasses import dataclass
from typing import Callable

from controle.acesso.controle_acesso import ControleAcesso
from controle.acesso.operacao import Operacao
from controle.sessao import Sessao
from entidade.perfil import Perfil
from entidade.usuario import Usuario

TITULOS_PAINEL = {
    Perfil.GESTOR: "PAINEL DO GESTOR",
    Perfil.FISCAL: "PAINEL DO FISCAL",
    Perfil.FUNCIONARIO: "PAINEL DO FUNCIONÁRIO",
}


@dataclass(frozen=True)
class AcaoDoPainel:
    operacao: Operacao
    rotulo: str
    executar: Callable[[], None]


class PainelFronteira:
    """Painel exibido após o login, com só as ações que o perfil permite.

    Cada funcionalidade se registra com `registrar`; o painel mostra as que
    o ControleAcesso liberar para o usuário (RF 03, C3). A conferência no
    controller continua valendo, mesmo que a opção fosse acionada por fora.
    """

    def __init__(self, sessao: Sessao, controle_acesso: ControleAcesso):
        self._sessao = sessao
        self._controle_acesso = controle_acesso
        self._acoes: list[AcaoDoPainel] = []

    def registrar(self, acao: AcaoDoPainel) -> None:
        self._acoes.append(acao)

    def abrir(self, usuario: Usuario) -> None:
        self._sessao.iniciar(usuario)
        try:
            print(f"\n===== {TITULOS_PAINEL[usuario.perfil]} =====")
            print(f"Bem-vindo(a), {usuario.nome}.")
            self._repetir_menu(self._acoes_permitidas(usuario))
        finally:
            self._sessao.encerrar()

    def _acoes_permitidas(self, usuario: Usuario) -> list[AcaoDoPainel]:
        return [acao for acao in self._acoes
                if self._controle_acesso.permite(usuario, acao.operacao)]

    def _repetir_menu(self, acoes: list[AcaoDoPainel]) -> None:
        while True:
            for numero, acao in enumerate(acoes, start=1):
                print(f"{numero} - {acao.rotulo}")
            print("0 - Sair")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "0":
                print("Saindo do painel...")
                return
            if not (opcao.isascii() and opcao.isdigit()
                    and 1 <= int(opcao) <= len(acoes)):
                print("Opção inválida. Tente novamente.")
                continue
            acoes[int(opcao) - 1].executar()
