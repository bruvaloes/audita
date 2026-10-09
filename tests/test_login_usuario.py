from dataclasses import replace

import pytest

from excecao.login_invalido_error import (
    LoginComNumerosError,
    LoginInvalidoError,
    LoginMuitoLongoError,
    LoginVazioError,
)


def adicionar_com_login(controller, dados_validos, login):
    return controller.adicionar(replace(dados_validos, login=login))


@pytest.mark.parametrize("login", ["maria", "a", "abcdefghijkl"])
def test_deve_aceitar_login_valido(controller, dados_validos, login):
    usuario = adicionar_com_login(controller, dados_validos, login)
    assert usuario.login == login


def test_deve_remover_espacos_nas_pontas_do_login(controller, dados_validos):
    usuario = adicionar_com_login(controller, dados_validos, "  maria  ")
    assert usuario.login == "maria"


@pytest.mark.parametrize("login", ["", "   "])
def test_deve_lancar_erro_quando_login_vazio(controller, dados_validos, login):
    with pytest.raises(LoginVazioError):
        adicionar_com_login(controller, dados_validos, login)


def test_deve_lancar_erro_quando_login_com_mais_de_12_caracteres(
        controller, dados_validos):
    with pytest.raises(LoginMuitoLongoError):
        adicionar_com_login(controller, dados_validos, "abcdefghijklm")


@pytest.mark.parametrize("login", ["maria1", "1maria", "123"])
def test_deve_lancar_erro_quando_login_contem_numeros(
        controller, dados_validos, login):
    with pytest.raises(LoginComNumerosError):
        adicionar_com_login(controller, dados_validos, login)


def test_erros_de_login_herdam_de_login_invalido_error(
        controller, dados_validos):
    with pytest.raises(LoginInvalidoError):
        adicionar_com_login(controller, dados_validos, "maria1")


def test_nao_deve_salvar_usuario_quando_login_invalido(
        controller, dados_validos):
    with pytest.raises(LoginInvalidoError):
        adicionar_com_login(controller, dados_validos, "maria1")
    assert controller.listar_todos() == []
