from typing import TYPE_CHECKING

from entidade.perfil import Perfil
from entidade.usuario import Usuario

if TYPE_CHECKING:
    from fronteira.contrato_fronteira import ContratoFronteira

TITULOS_PAINEL = {
    Perfil.GESTOR: "PAINEL DO GESTOR",
    Perfil.FISCAL: "PAINEL DO FISCAL",
    Perfil.FUNCIONARIO: "PAINEL DO FUNCIONÁRIO",
}


class PainelFronteira:
    """Painel exibido após o login, conforme o perfil do usuário."""

    def __init__(self, contrato_fronteira: "ContratoFronteira | None" = None):
        self._contrato_fronteira = contrato_fronteira

    def abrir(self, usuario: Usuario) -> None:
        print(f"\n===== {TITULOS_PAINEL[usuario.perfil]} =====")
        print(f"Bem-vindo(a), {usuario.nome}.")
        while True:
            if usuario.perfil == Perfil.GESTOR and self._contrato_fronteira:
                print("1 - Gerenciar contratos")
                print("0 - Sair")
                opcao = input("Escolha uma opção: ").strip()
                if opcao == "0":
                    print("Saindo do painel...")
                    return
                elif opcao == "1":
                    self._contrato_fronteira.menu(usuario)
                else:
                    print("Opção inválida. Tente novamente.")
            elif self._contrato_fronteira and usuario.perfil in (Perfil.FISCAL, Perfil.FUNCIONARIO):
                print("1 - Meus contratos vinculados")
                print("0 - Sair")
                opcao = input("Escolha uma opção: ").strip()
                if opcao == "0":
                    print("Saindo do painel...")
                    return
                elif opcao == "1":
                    self._contrato_fronteira.listar_contratos(usuario)
                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("0 - Sair")
                if input("Escolha uma opção: ").strip() == "0":
                    print("Saindo do painel...")
                    return
                print("Opção inválida. Tente novamente.")
