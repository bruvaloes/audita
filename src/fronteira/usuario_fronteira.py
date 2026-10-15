from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.usuario_controller import UsuarioController
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.persistencia_error import PersistenciaError
from excecao.validacao_error import ValidacaoError

LARGURA_TABELA = 75


class UsuarioFronteira:

    def __init__(self, controller: UsuarioController):
        self._controller = controller
        self._opcoes_menu = {
            "1": self.cadastrar_usuario,
            "2": self.listar_usuarios,
        }

    def menu(self) -> None:
        while True:
            self._exibir_menu()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "0":
                print("Encerrando...")
                return

            acao = self._opcoes_menu.get(opcao)
            if acao is None:
                print("Opção inválida. Tente novamente.")
                continue
            acao()

    def cadastrar_usuario(self) -> None:
        print("\n--- Cadastro de Usuário ---")
        dados = self._ler_dados_cadastro()

        try:
            usuario = self._controller.adicionar(dados)
        except ValidacaoError as erro:
            print(f"\nErro ao cadastrar: {erro}")
            return
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")
            return

        print("\nUsuário cadastrado com sucesso!")
        print(f"   {usuario}")

    def listar_usuarios(self) -> None:
        try:
            usuarios = self._controller.listar_todos()
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")
            return

        if not usuarios:
            print("\nNenhum usuário cadastrado.")
            return

        self._exibir_tabela(usuarios)

    def _exibir_menu(self) -> None:
        print("\n===== GERENCIAMENTO DE USUÁRIOS =====")
        print("1 - Cadastrar usuário")
        print("2 - Listar usuários")
        print("0 - Sair")

    def _ler_dados_cadastro(self) -> DadosCadastroUsuario:
        nome = input("Nome: ").strip()
        cpf = input("CPF (11 dígitos): ").strip()
        email = input("E-mail: ").strip()
        login = input("Login: ").strip()
        senha = input("Senha: ").strip()

        print(f"Perfis disponíveis: {Perfil.nomes_validos()}")
        perfil = input("Perfil: ").strip()

        return DadosCadastroUsuario(nome, cpf, email, login, senha, perfil)

    def _exibir_tabela(self, usuarios: list[Usuario]) -> None:
        print("\n--- Lista de Usuários ---")
        print(f"{'ID':<5} {'Nome':<20} {'E-mail':<25} "
              f"{'Perfil':<15} {'Situação':<10}")
        print("-" * LARGURA_TABELA)
        for usuario in usuarios:
            print(f"{usuario.id:<5} {usuario.nome:<20} {usuario.email:<25} "
                  f"{usuario.perfil.value:<15} {usuario.situacao:<10}")
        print(f"\nTotal: {len(usuarios)} usuário(s)")
