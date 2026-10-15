import sqlite3

import pytest

from controle.dados_cadastro_usuario import DadosCadastroUsuario
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
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite


@pytest.fixture
def controller(tmp_path):
    repositorio = UsuarioRepositorioSQLite(str(tmp_path / "teste.db"))
    return UsuarioController(repositorio, ValidadorCadastroUsuario(repositorio))


def adicionar(controller, cpf, email, login):
    return controller.adicionar(DadosCadastroUsuario(
        nome="Fulano",
        cpf=cpf,
        email=email,
        login=login,
        senha="SenhaValida1!",
        perfil="GESTOR",
    ))


def test_login_duplicado_lanca_escrita_persistencia_error(controller):
    adicionar(controller, "12345678901", "a@x.com", "fulano")
    with pytest.raises(EscritaPersistenciaError):
        adicionar(controller, "12345678902", "b@x.com", "fulano")


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
