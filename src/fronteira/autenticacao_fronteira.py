from getpass import getpass
from typing import TYPE_CHECKING, Callable

from controle.autenticacao_controller import AutenticacaoController
from entidade.perfil import Perfil
from excecao.credenciais_invalidas_error import CredenciaisInvalidasError
from excecao.persistencia_error import PersistenciaError
from fronteira.painel_fronteira import PainelFronteira

if TYPE_CHECKING:
    from controle.facade_singleton_controller import FacadeSingletonController


class AutenticacaoFronteira:

    def __init__(self, controller: "FacadeSingletonController | AutenticacaoController",
                 painel: PainelFronteira,
                 ler_senha: Callable[[str], str] = getpass):
        self._controller = controller
        self._painel = painel
        self._ler_senha = ler_senha

    def entrar(self) -> None:
        print("\n--- Login ---")
        identificador = input("Login, CPF (só números) ou e-mail: ").strip()
        senha = self._ler_senha("Senha: ").strip()
        print(f"Perfis disponíveis: {Perfil.nomes_validos()}")
        perfil = input("Perfil: ").strip()

        try:
            usuario = self._controller.autenticar(identificador, senha, perfil)
        except CredenciaisInvalidasError as erro:
            print(f"\n{erro}")
            return
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")
            return

        self._painel.abrir(usuario)
