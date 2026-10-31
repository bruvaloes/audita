from controle.acesso.controle_acesso import ControleAcesso
from controle.acesso.operacao import Operacao
from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController
from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
from controle.sessao import Sessao
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from excecao.persistencia_error import PersistenciaError
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.contrato_fronteira import ContratoFronteira
from fronteira.painel_fronteira import AcaoDoPainel, PainelFronteira
from fronteira.usuario_fronteira import UsuarioFronteira
from log.log_auditoria import LogAuditoria
from log.log_auditoria_adapter import LogAuditoriaAdapter
from log.log_auditoria_memoria import LogAuditoriaMemoria
from persistencia.acesso_repositorio import AcessoRepositorio
from persistencia.acesso_repositorio_memoria import AcessoRepositorioMemoria
from persistencia.acesso_repositorio_sqlite import AcessoRepositorioSQLite
from persistencia.contrato_repositorio import ContratoRepositorio
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.contrato_repositorio_sqlite import ContratoRepositorioSQLite
from persistencia.evidencia_repositorio import EvidenciaRepositorio
from persistencia.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from persistencia.evidencia_repositorio_sqlite import EvidenciaRepositorioSQLite
from persistencia.usuario_repositorio import UsuarioRepositorio
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite

# Para oferecer outro mecanismo de armazenamento, basta incluir uma entrada:
# opção -> (descrição no menu, fábrica do repositório de usuários, fábrica do
# repositório de acessos, fábrica do repositório de contratos, fábrica do repositório
# de evidências, fábrica do log de auditoria).
MECANISMOS_ARMAZENAMENTO = {
    "1": (
        "Banco de dados (SQLite)",
        UsuarioRepositorioSQLite,
        AcessoRepositorioSQLite,
        ContratoRepositorioSQLite,
        EvidenciaRepositorioSQLite,
        lambda: LogAuditoriaAdapter("auditoria.log"),
    ),
    "2": (
        "Em memória",
        UsuarioRepositorioMemoria,
        AcessoRepositorioMemoria,
        ContratoRepositorioMemoria,
        EvidenciaRepositorioMemoria,
        LogAuditoriaMemoria,
    ),
}


def escolher_repositorios() -> tuple[
    UsuarioRepositorio,
    AcessoRepositorio,
    ContratoRepositorio,
    EvidenciaRepositorio,
    LogAuditoria,
]:
    print("===== CONFIGURAÇÃO DE PERSISTÊNCIA =====")
    for opcao, (descricao, *_) in MECANISMOS_ARMAZENAMENTO.items():
        print(f"{opcao} - {descricao}")

    while True:
        opcao = input("Escolha o mecanismo de armazenamento: ").strip()
        if opcao not in MECANISMOS_ARMAZENAMENTO:
            print("\nOpção inválida. Tente novamente.")
            continue

        (
            descricao,
            criar_usuarios,
            criar_acessos,
            criar_contratos,
            criar_evidencias,
            criar_log,
        ) = MECANISMOS_ARMAZENAMENTO[opcao]
        try:
            repositorios = (
                criar_usuarios(),
                criar_acessos(),
                criar_contratos(),
                criar_evidencias(),
                criar_log(),
            )
        except PersistenciaError as erro:
            print(f"\n{erro}\nEscolha outro mecanismo de armazenamento.")
            continue
        print(f"Usando: {descricao}\n")
        return repositorios


def main():
    """Raiz de composição: único lugar que escolhe as implementações."""
    (
        usuario_repo,
        acesso_repo,
        contrato_repo,
        evidencia_repo,
        log_auditoria,
    ) = escolher_repositorios()

    hash_senha = HashSenhaArgon2()
    controle_acesso = ControleAcesso()
    sessao = Sessao()
    validador_usuario = ValidadorCadastroUsuario(usuario_repo)
    controller_usuario = UsuarioController(
        usuario_repo, validador_usuario, hash_senha, controle_acesso,
        log=log_auditoria)
    autenticacao = AutenticacaoController(usuario_repo, acesso_repo, hash_senha)

    contrato_controller = ContratoController(
        repositorio=contrato_repo,
        controle_acesso=controle_acesso,
        evidencia_repositorio=evidencia_repo,
        usuario_repositorio=usuario_repo,
        log=log_auditoria,
    )
    contrato_fronteira = ContratoFronteira(contrato_controller, sessao)
    painel = PainelFronteira(sessao, controle_acesso)

    fronteira = UsuarioFronteira(
        controller_usuario, AutenticacaoFronteira(autenticacao, painel),
        sessao)
    painel.registrar(AcaoDoPainel(
        Operacao.LISTAR_USUARIOS, "Listar usuários",
        fronteira.listar_usuarios))
    for operacao, rotulo, acao in (
        (Operacao.CADASTRAR_CONTRATO, "Cadastrar contrato",
         contrato_fronteira.cadastrar_contrato),
        (Operacao.LISTAR_CONTRATOS, "Listar contratos",
         contrato_fronteira.listar_contratos),
        (Operacao.EDITAR_CONTRATO, "Editar contrato",
         contrato_fronteira.editar_contrato),
        (Operacao.EDITAR_CONTRATO, "Encerrar contrato",
         contrato_fronteira.encerrar_contrato),
        (Operacao.REMOVER_CONTRATO, "Remover contrato",
         contrato_fronteira.remover_contrato),
        (Operacao.VINCULAR_USUARIO_CONTRATO, "Vincular usuário a contrato",
         contrato_fronteira.vincular_usuario),
        (Operacao.VINCULAR_USUARIO_CONTRATO, "Desvincular usuário de contrato",
         contrato_fronteira.desvincular_usuario),
    ):
        painel.registrar(AcaoDoPainel(operacao, rotulo, acao))
    fronteira.menu()


if __name__ == "__main__":
    main()
