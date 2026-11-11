from datetime import date, datetime
import sqlite3

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from excecao.persistencia_error import (
    ConexaoPersistenciaError,
    EscritaPersistenciaError,
    LeituraPersistenciaError,
    PersistenciaError,
)
from entidade.acesso import Acesso
from entidade.contrato import Contrato
from entidade.evidencia import Evidencia
from entidade.origem_evidencia import OrigemEvidencia
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from entidade.situacao_contrato import SituacaoContrato
from entidade.situacao_validacao import SituacaoValidacao
from entidade.usuario import Usuario
from excecao.validacao_error import UsuarioDuplicadoError
from infraestrutura.repositorio_factory import RepositorioFactorySQLite
from infraestrutura.usuario_repositorio_sqlite import UsuarioRepositorioSQLite


@pytest.fixture
def controller(tmp_path):
    repositorio = UsuarioRepositorioSQLite(str(tmp_path / "teste.db"))
    hash_senha = HashSenhaArgon2(custo_tempo=1, custo_memoria_kib=8,
                                 paralelismo=1)
    return UsuarioController(
        repositorio, ValidadorCadastroUsuario(repositorio), hash_senha,
        ControleAcesso())


def adicionar(controller, cpf, email, login):
    return controller.adicionar(DadosCadastroUsuario(
        nome="Fulano",
        cpf=cpf,
        email=email,
        login=login,
        senha="SenhaValida1!",
        confirmacao_senha="SenhaValida1!",
        perfil="GESTOR",
        aceite_termos="s",
    ))


def test_login_duplicado_no_banco_lanca_escrita_persistencia_error(tmp_path):
    repositorio = UsuarioRepositorioSQLite(str(tmp_path / "teste.db"))
    repositorio.salvar(Usuario(0, "A", "1", "a@x.com", "fulano", "h", Perfil.GESTOR))
    with pytest.raises(EscritaPersistenciaError):
        repositorio.salvar(
            Usuario(0, "B", "2", "b@x.com", "fulano", "h", Perfil.GESTOR))


def test_login_duplicado_no_cadastro_lanca_erro_de_validacao(controller):
    adicionar(controller, "52998224725", "a@x.com", "fulano")
    with pytest.raises(UsuarioDuplicadoError) as erro:
        adicionar(controller, "11144477735", "b@x.com", "fulano")
    assert str(erro.value) == "Login já cadastrado"


def test_banco_inacessivel_lanca_conexao_persistencia_error(tmp_path):
    with pytest.raises(ConexaoPersistenciaError):
        UsuarioRepositorioSQLite(str(tmp_path / "inexistente" / "teste.db"))


def test_tabela_inexistente_lanca_leitura_persistencia_error(tmp_path):
    caminho = str(tmp_path / "teste.db")
    repositorio = UsuarioRepositorioSQLite(caminho)
    with sqlite3.connect(caminho) as conn:
        conn.execute("DROP TABLE usuarios")
    with pytest.raises(LeituraPersistenciaError):
        repositorio.listar_todos()


@pytest.mark.parametrize("excecao", [
    ConexaoPersistenciaError,
    LeituraPersistenciaError,
    EscritaPersistenciaError,
])
def test_excecoes_herdam_de_persistencia_error(excecao):
    assert issubclass(excecao, PersistenciaError)


def test_reinicio_persistencia_sqlite_mantem_dados_identicos(tmp_path):
    """NF001 de Confiabilidade: criar ao menos 1 registro de cada entidade
    (Usuario, Contrato, Evidencia e Acesso) no SQLite, reabrir o banco
    (nova fábrica) e conferir que os dados continuam idênticos.
    """
    db_usuarios = str(tmp_path / "usuarios.db")
    db_contratos = str(tmp_path / "contratos.db")
    db_evidencias = str(tmp_path / "evidencias.db")
    caminho_log = str(tmp_path / "auditoria.log")

    # 1. Primeira inicialização e gravação de 1 registro por entidade
    fabrica_original = RepositorioFactorySQLite(
        db_usuarios=db_usuarios,
        db_contratos=db_contratos,
        db_evidencias=db_evidencias,
        caminho_log=caminho_log,
    )
    usuario_repo_1 = fabrica_original.criar_usuario_repositorio()
    acesso_repo_1 = fabrica_original.criar_acesso_repositorio()
    contrato_repo_1 = fabrica_original.criar_contrato_repositorio()
    evidencia_repo_1 = fabrica_original.criar_evidencia_repositorio()

    momento = datetime(2026, 11, 10, 14, 30, 0)
    usuario = Usuario(
        id=0,
        nome="Mariana Alves",
        cpf="52998224725",
        email="mariana@email.com",
        login="mariana",
        senha_hash="hash_argon2_valido",
        perfil=Perfil.GESTOR,
        ativo=True,
        aceite_termos_em=momento,
    )
    usuario_salvo = usuario_repo_1.salvar(usuario)

    acesso = Acesso(
        id=0,
        usuario_id=usuario_salvo.id,
        perfil=Perfil.GESTOR,
        data_hora=momento,
        resultado=ResultadoAcesso.SUCESSO,
    )
    acesso_salvo = acesso_repo_1.salvar(acesso)

    contrato = Contrato(
        id=0,
        numero="CT-2026-999",
        empresa_contratada="Alpha Soluções",
        vigencia_inicio=date(2026, 1, 1),
        vigencia_fim=date(2026, 12, 31),
        arquivo="contrato_final.pdf",
        situacao=SituacaoContrato.ATIVO,
        usuarios_vinculados=[usuario_salvo.id],
    )
    contrato_salvo = contrato_repo_1.salvar(contrato)

    evidencia = Evidencia(
        id=0,
        caminho_imagem="storage/foto_999.jpg",
        enviada_em=momento,
        geolocalizacao="-23.550520,-46.633308",
        origem=OrigemEvidencia.CAMERA,
        situacao=SituacaoValidacao.PENDENTE,
        id_funcionario=usuario_salvo.id,
        numero_contrato=contrato_salvo.numero,
        nome_tarefa="Manutenção Elétrica",
    )
    evidencia_salva = evidencia_repo_1.salvar(evidencia)

    # 2. "Reinício": descarta instâncias antigas e reabre os bancos
    del fabrica_original, usuario_repo_1, acesso_repo_1, contrato_repo_1, evidencia_repo_1

    fabrica_reiniciada = RepositorioFactorySQLite(
        db_usuarios=db_usuarios,
        db_contratos=db_contratos,
        db_evidencias=db_evidencias,
        caminho_log=caminho_log,
    )
    usuario_repo_2 = fabrica_reiniciada.criar_usuario_repositorio()
    acesso_repo_2 = fabrica_reiniciada.criar_acesso_repositorio()
    contrato_repo_2 = fabrica_reiniciada.criar_contrato_repositorio()
    evidencia_repo_2 = fabrica_reiniciada.criar_evidencia_repositorio()

    # 3. Conferência de que todos os dados continuam idênticos
    usuario_recuperado = usuario_repo_2.buscar_por_cpf("52998224725")
    assert usuario_recuperado == usuario_salvo
    assert usuario_recuperado.login == "mariana"
    assert usuario_recuperado.perfil == Perfil.GESTOR
    assert usuario_recuperado.aceite_termos_em == momento

    acessos_recuperados = acesso_repo_2.listar_todos()
    assert len(acessos_recuperados) == 1
    assert acessos_recuperados[0] == acesso_salvo

    contrato_recuperado = contrato_repo_2.buscar_por_numero("CT-2026-999")
    assert contrato_recuperado == contrato_salvo
    assert contrato_recuperado.empresa_contratada == "Alpha Soluções"
    assert contrato_recuperado.usuarios_vinculados == [usuario_salvo.id]

    evidencia_recuperada = evidencia_repo_2.buscar_por_id(evidencia_salva.id)
    assert evidencia_recuperada == evidencia_salva
    assert evidencia_recuperada.nome_tarefa == "Manutenção Elétrica"
    assert evidencia_recuperada.situacao == SituacaoValidacao.PENDENTE


