from controle.usuario_controller import UsuarioController
from entidade.perfil import Perfil
from excecao.login_invalido_error import LoginInvalidoError


class UsuarioFronteira:

    def __init__(self, controller: UsuarioController):
        self._controller = controller

    def menu(self) -> None:
        while True:
            print("\n===== GERENCIAMENTO DE USUÁRIOS =====")
            print("1 - Cadastrar usuário")
            print("2 - Listar usuários")
            print("0 - Sair")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self.cadastrar_usuario()
            elif opcao == "2":
                self.listar_usuarios()
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
        login = input("Login: ").strip()
        senha = input("Senha: ").strip()

        perfis_disponiveis = ", ".join(p.value for p in Perfil)
        print(f"Perfis disponíveis: {perfis_disponiveis}")
        perfil_str = input("Perfil: ").strip()

        try:
            usuario = self._controller.adicionar(
                nome, cpf, email, login, senha, perfil_str
            )
            print(f"\nUsuário cadastrado com sucesso!")
            print(f"   {usuario}")
        except LoginInvalidoError as e:
            print(f"\nLogin inválido: {e}")
        except ValueError as e:
            print(f"\nErro ao cadastrar: {e}")

    def listar_usuarios(self) -> None:
        usuarios = self._controller.listar_todos()

        if not usuarios:
            print("\nNenhum usuário cadastrado.")
            return

        print("\n--- Lista de Usuários ---")
        print(f"{'ID':<5} {'Nome':<20} {'E-mail':<25} {'Perfil':<15} {'Situação':<10}")
        print("-" * 75)
        for u in usuarios:
            situacao = "Ativo" if u.ativo else "Inativo"
            print(f"{u.id:<5} {u.nome:<20} {u.email:<25} {u.perfil.value:<15} {situacao:<10}")
        print(f"\nTotal: {len(usuarios)} usuário(s)")
