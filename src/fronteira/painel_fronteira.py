from entidade.perfil import Perfil
from entidade.usuario import Usuario

TITULOS_PAINEL = {
    Perfil.GESTOR: "PAINEL DO GESTOR",
    Perfil.FISCAL: "PAINEL DO FISCAL",
    Perfil.FUNCIONARIO: "PAINEL DO FUNCIONÁRIO",
}


class PainelFronteira:
    """Painel exibido após o login, conforme o perfil do usuário.

    Por enquanto só identifica o perfil e permite sair; as funções de cada
    painel (contratos, evidências etc.) entram nas issues próprias.
    """

    def abrir(self, usuario: Usuario) -> None:
        print(f"\n===== {TITULOS_PAINEL[usuario.perfil]} =====")
        print(f"Bem-vindo(a), {usuario.nome}.")
        while True:
            print("0 - Sair")
            if input("Escolha uma opção: ").strip() == "0":
                print("Saindo do painel...")
                return
            print("Opção inválida. Tente novamente.")
