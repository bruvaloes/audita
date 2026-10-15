from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from excecao.persistencia_error import PersistenciaError
from fronteira.usuario_fronteira import UsuarioFronteira
from persistencia.usuario_repositorio import UsuarioRepositorio
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite

# Para oferecer outro mecanismo de armazenamento, basta incluir uma entrada:
# opção -> (descrição no menu, fábrica do repositório).
MECANISMOS_ARMAZENAMENTO = {
    "1": ("Banco de dados (SQLite)", UsuarioRepositorioSQLite),
    "2": ("Em memória", UsuarioRepositorioMemoria),
}


def escolher_repositorio() -> UsuarioRepositorio:
    print("===== CONFIGURAÇÃO DE PERSISTÊNCIA =====")
    for opcao, (descricao, _) in MECANISMOS_ARMAZENAMENTO.items():
        print(f"{opcao} - {descricao}")

    while True:
        opcao = input("Escolha o mecanismo de armazenamento: ").strip()
        if opcao not in MECANISMOS_ARMAZENAMENTO:
            print("\nOpção inválida. Tente novamente.")
            continue

        descricao, criar_repositorio = MECANISMOS_ARMAZENAMENTO[opcao]
        try:
            repositorio = criar_repositorio()
        except PersistenciaError as erro:
            print(f"\n{erro}\nEscolha outro mecanismo de armazenamento.")
            continue
        print(f"Usando: {descricao}\n")
        return repositorio


def main():
    """Raiz de composição: único lugar que escolhe as implementações."""
    repositorio = escolher_repositorio()
    validador = ValidadorCadastroUsuario(repositorio)
    controller = UsuarioController(repositorio, validador)
    fronteira = UsuarioFronteira(controller)
    fronteira.menu()


if __name__ == "__main__":
    main()
