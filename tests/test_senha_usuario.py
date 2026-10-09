from dataclasses import replace

import pytest

from excecao.senha_invalida_error import (
    SenhaInvalidaError,
    SenhaMuitoCurtaError,
    SenhaMuitoLongaError,
    SenhaSemCaractereEspecialError,
    SenhaSemMaiusculaError,
    SenhaSemMinusculaError,
    SenhaSemNumeroError,
)
from controle.validacao.validador_senha import TAMANHO_MAXIMO_SENHA


@pytest.fixture
def adicionar(controller, dados_validos):
    def _adicionar(senha):
        return controller.adicionar(replace(dados_validos, senha=senha))
    return _adicionar


@pytest.mark.parametrize("senha", ["Senha@123", "P4ssw0rd!", "A1#bcdefgh", "Senh4_F0rt3("])
def test_deve_aceitar_senha_valida(adicionar, senha):
    assert adicionar(senha).senha == senha


@pytest.mark.parametrize("senha", ["1@Abcde", "S@1abcd"])  # 7 caracteres
def test_deve_lancar_erro_quando_senha_muito_curta(adicionar, senha):
    with pytest.raises(SenhaMuitoCurtaError):
        adicionar(senha)


def test_deve_lancar_erro_quando_senha_muito_longa(adicionar):
    with pytest.raises(SenhaMuitoLongaError):
        # Cria uma senha com 129 caracteres (1 caractere a mais que o máximo permitido)
        senha_longa = "S@1a" + ("b" * (TAMANHO_MAXIMO_SENHA - 3))
        adicionar(senha_longa)


@pytest.mark.parametrize("senha", ["senha@1234", "minha_senha1"])
def test_deve_lancar_erro_quando_senha_sem_maiuscula(adicionar, senha):
    with pytest.raises(SenhaSemMaiusculaError):
        adicionar(senha)


@pytest.mark.parametrize("senha", ["SENHA@1234", "MINHA_SENHA1"])
def test_deve_lancar_erro_quando_senha_sem_minuscula(adicionar, senha):
    with pytest.raises(SenhaSemMinusculaError):
        adicionar(senha)


@pytest.mark.parametrize("senha", ["Senha@Forte", "Outra$Senha"])
def test_deve_lancar_erro_quando_senha_sem_numero(adicionar, senha):
    with pytest.raises(SenhaSemNumeroError):
        adicionar(senha)


@pytest.mark.parametrize("senha", ["Senha12345", "S3nhaForte"])
def test_deve_lancar_erro_quando_senha_sem_caractere_especial(adicionar, senha):
    with pytest.raises(SenhaSemCaractereEspecialError):
        adicionar(senha)


def test_erros_de_senha_herdam_de_senha_invalida_error(adicionar):
    with pytest.raises(SenhaInvalidaError):
        adicionar("fraca")

def test_nao_deve_salvar_usuario_quando_senha_invalida(adicionar, controller):
    with pytest.raises(SenhaInvalidaError):
        adicionar("fraca")
    assert controller.listar_todos() == []
