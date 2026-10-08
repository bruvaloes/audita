from persistencia.usuario_repositorio import UsuarioRepositorioMemoria
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite
from controle.usuario_controller import UsuarioController
from fronteira.usuario_fronteira import UsuarioFronteira
from excecao.persistencia_error import PersistenciaError


def escolher_repositorio():
    print("===== CONFIGURAÇÃO DE PERSISTÊNCIA =====")
    print("1 - Banco de dados (SQLite)")
    print("2 - Em memória")

    while True:
        opcao = input("Escolha o mecanismo de armazenamento: ").strip()
        if opcao == "1":
            try:
                repositorio = UsuarioRepositorioSQLite()
            except PersistenciaError as e:
                print(f"\n{e}\nEscolha outro mecanismo de armazenamento.")
                continue
            print("Usando banco de dados (SQLite)\n")
            return repositorio
        elif opcao == "2":
            print("Usando memória\n")
            return UsuarioRepositorioMemoria()
        else:
            print("\nOpção inválida. Tente novamente.")


def main():
    repositorio = escolher_repositorio()
    controller = UsuarioController(repositorio)
    fronteira = UsuarioFronteira(controller)
    fronteira.menu()


if __name__ == "__main__":
    main()
