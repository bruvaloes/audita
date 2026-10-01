from controle.usuario_controller import UsuarioController
from entidade.perfil import Perfil


class UsuarioFronteira:

    def __init__(self, controller: UsuarioController):
        self._controller = controller

    def menu(self) -> None:
        while True:
            print("\n===== GERENCIAMENTO DE USUÁRIOS =====")
            print("1 - Cadastrar usuário")
            print("0 - Sair")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self.cadastrar_usuario()
            elif opcao == "0":
                print("Encerrando...")
                break
            else:
                print("Opção inválida. Tente novamente.")

    def cadastrar_usuario(self) -> None:
        print("\n--- Cadastro de Usuário ---")
        nome = input("Nome: ").strip()
        cpf = input("CPF (11 dígitos): ").strip()
        email = input("E-mail: ").strip()
        senha = input("Senha: ").strip()

        perfis_disponiveis = ", ".join(p.value for p in Perfil)
        print(f"Perfis disponíveis: {perfis_disponiveis}")
        perfil_str = input("Perfil: ").strip()

        try:
            usuario = self._controller.adicionar(nome, cpf, email, senha, perfil_str)
            print(f"\nUsuário cadastrado com sucesso!")
            print(f"   {usuario}")
        except ValueError as e:
            print(f"\nErro ao cadastrar: {e}")
