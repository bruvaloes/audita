from controle.autenticacao_controller import AutenticacaoController
from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from excecao.persistencia_error import PersistenciaError
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.painel_fronteira import PainelFronteira
from fronteira.usuario_fronteira import UsuarioFronteira
from persistencia.acesso_repositorio import AcessoRepositorio
from persistencia.acesso_repositorio_memoria import AcessoRepositorioMemoria
from persistencia.acesso_repositorio_sqlite import AcessoRepositorioSQLite
from persistencia.usuario_repositorio import UsuarioRepositorio
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite

# Para oferecer outro mecanismo de armazenamento, basta incluir uma entrada:
# opção -> (descrição no menu, fábrica do repositório de usuários, fábrica do
# repositório de acessos).
MECANISMOS_ARMAZENAMENTO = {
    "1": ("Banco de dados (SQLite)", UsuarioRepositorioSQLite,
          AcessoRepositorioSQLite),
    "2": ("Em memória", UsuarioRepositorioMemoria, AcessoRepositorioMemoria),
}


def escolher_repositorios() -> tuple[UsuarioRepositorio, AcessoRepositorio]:
    print("===== CONFIGURAÇÃO DE PERSISTÊNCIA =====")
    for opcao, (descricao, *_) in MECANISMOS_ARMAZENAMENTO.items():
        print(f"{opcao} - {descricao}")

    while True:
        opcao = input("Escolha o mecanismo de armazenamento: ").strip()
        if opcao not in MECANISMOS_ARMAZENAMENTO:
            print("\nOpção inválida. Tente novamente.")
            continue

        descricao, criar_usuarios, criar_acessos = \
            MECANISMOS_ARMAZENAMENTO[opcao]
        try:
            repositorios = criar_usuarios(), criar_acessos()
        except PersistenciaError as erro:
            print(f"\n{erro}\nEscolha outro mecanismo de armazenamento.")
            continue
        print(f"Usando: {descricao}\n")
        return repositorios


def main():
    """Raiz de composição: único lugar que escolhe as implementações."""
    repositorio, acessos = escolher_repositorios()
    hash_senha = HashSenhaArgon2()
    validador = ValidadorCadastroUsuario(repositorio)
    controller = UsuarioController(repositorio, validador, hash_senha)
    autenticacao = AutenticacaoController(repositorio, acessos, hash_senha)
    fronteira = UsuarioFronteira(
        controller,
        AutenticacaoFronteira(autenticacao, PainelFronteira()),
    )
    fronteira.menu()


if __name__ == "__main__":
    main()
