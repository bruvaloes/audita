import sqlite3

import pytest

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
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.validacao_error import UsuarioDuplicadoError
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite


@pytest.fixture
def controller(tmp_path):
    repositorio = UsuarioRepositorioSQLite(str(tmp_path / "teste.db"))
    hash_senha = HashSenhaArgon2(custo_tempo=1, custo_memoria_kib=8,
                                 paralelismo=1)
    return UsuarioController(
        repositorio, ValidadorCadastroUsuario(repositorio), hash_senha)


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
