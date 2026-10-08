import pytest

from controle.usuario_controller import UsuarioController
from entidade.perfil import Perfil
from excecao.login_invalido_error import (
    LoginComNumerosError,
    LoginInvalidoError,
    LoginMuitoLongoError,
    LoginVazioError,
)
from persistencia.usuario_repositorio import UsuarioRepositorio


@pytest.fixture
def controller():
    return UsuarioController(UsuarioRepositorio())


def adicionar(controller, login):
    return controller.adicionar(
        "Maria", "12345678900", "maria@email.com", login, "Senha@123",
        next(iter(Perfil)).value
    )


@pytest.mark.parametrize("login", ["maria", "a", "abcdefghijkl"])
def test_deve_aceitar_login_valido(controller, login):
    assert adicionar(controller, login).login == login


def test_deve_remover_espacos_nas_pontas_do_login(controller):
    assert adicionar(controller, "  maria  ").login == "maria"


@pytest.mark.parametrize("login", ["", "   "])
def test_deve_lancar_erro_quando_login_vazio(controller, login):
    with pytest.raises(LoginVazioError):
        adicionar(controller, login)


def test_deve_lancar_erro_quando_login_com_mais_de_12_caracteres(controller):
    with pytest.raises(LoginMuitoLongoError):
        adicionar(controller, "abcdefghijklm")


@pytest.mark.parametrize("login", ["maria1", "1maria", "123"])
def test_deve_lancar_erro_quando_login_contem_numeros(controller, login):
    with pytest.raises(LoginComNumerosError):
        adicionar(controller, login)


def test_erros_de_login_herdam_de_login_invalido_error(controller):
    with pytest.raises(LoginInvalidoError):
        adicionar(controller, "maria1")


def test_nao_deve_salvar_usuario_quando_login_invalido(controller):
    with pytest.raises(LoginInvalidoError):
        adicionar(controller, "maria1")
    assert controller.listar_todos() == []
