from dataclasses import replace

import pytest

from controle.validacao.validador_senha import (
    DESCRICAO_POLITICA,
    TAMANHO_MAXIMO_SENHA,
    TAMANHO_MINIMO_SENHA,
)
from excecao.senha_invalida_error import (
    SenhaComPoucosTiposError,
    SenhaIgualLoginError,
    SenhaInvalidaError,
    SenhaMuitoCurtaError,
    SenhaMuitoLongaError,
    SenhasDiferentesError,
)

MENSAGEM_POLITICA = (
    "Senha: use 8 a 128 caracteres e 3 destes tipos: maiúscula, minúscula, "
    "número, especial"
)


@pytest.fixture
def adicionar(controller, dados_validos):
    def _adicionar(senha):
        return controller.adicionar(
            replace(dados_validos, senha=senha, confirmacao_senha=senha))
    return _adicionar


@pytest.mark.parametrize("senha", [
    "Senha@123",      # 4 tipos
    "P4ssw0rd!",
    "Abcdefg1",       # 3 tipos: maiúscula, minúscula e número
    "abcdef1!",       # 3 tipos: minúscula, número e especial
    "ABCDEF1!",       # 3 tipos: maiúscula, número e especial
    "Abcdefg!",       # 3 tipos: maiúscula, minúscula e especial
])
def test_deve_aceitar_senha_com_3_ou_4_tipos(adicionar, senha):
    assert adicionar(senha).id == 1


@pytest.mark.parametrize("senha", ["abcdefgh1", "ABCDEFGH!", "12345678", "abcdefgh"])
def test_deve_lancar_erro_quando_senha_tem_menos_de_3_tipos(adicionar, senha):
    with pytest.raises(SenhaComPoucosTiposError):
        adicionar(senha)


def test_deve_aceitar_senha_no_tamanho_minimo(adicionar):
    assert adicionar("Aa1!" + "b" * (TAMANHO_MINIMO_SENHA - 4)).id == 1


@pytest.mark.parametrize("senha", ["Aa1!bcd", "1@Abcde"])  # 7 caracteres
def test_deve_lancar_erro_quando_senha_muito_curta(adicionar, senha):
    with pytest.raises(SenhaMuitoCurtaError):
        adicionar(senha)


def test_deve_aceitar_senha_no_tamanho_maximo(adicionar):
    assert adicionar("Aa1!" + "b" * (TAMANHO_MAXIMO_SENHA - 4)).id == 1


def test_deve_lancar_erro_quando_senha_muito_longa(adicionar):
    with pytest.raises(SenhaMuitoLongaError):
        adicionar("Aa1!" + "b" * (TAMANHO_MAXIMO_SENHA - 3))  # 129 caracteres


@pytest.mark.parametrize("senha", ["Aa1!bcd", "abcdefgh1", "Aa1!" + "b" * 125])
def test_mensagem_deve_resumir_a_politica_completa(adicionar, senha):
    with pytest.raises(SenhaInvalidaError) as erro:
        adicionar(senha)
    assert str(erro.value) == MENSAGEM_POLITICA
    assert len(str(erro.value)) <= 120


def test_descricao_da_politica_deve_citar_os_limites():
    assert "8 a 128" in DESCRICAO_POLITICA
    assert "3 destes tipos" in DESCRICAO_POLITICA


def test_nao_deve_salvar_usuario_quando_senha_invalida(adicionar, controller, repositorio):
    with pytest.raises(SenhaInvalidaError):
        adicionar("fraca")
    assert repositorio.listar_todos() == []


def test_deve_lancar_erro_quando_confirmacao_difere_da_senha(controller, dados_validos, repositorio):
    dados = replace(dados_validos, confirmacao_senha="Senha@124")
    with pytest.raises(SenhasDiferentesError) as erro:
        controller.adicionar(dados)
    assert str(erro.value) == "As senhas não coincidem"
    assert repositorio.listar_todos() == []


def test_deve_lancar_erro_quando_senha_igual_ao_login(controller, dados_validos, repositorio):
    dados = replace(dados_validos, login="Senha@Forte",
                    senha="Senha@Forte", confirmacao_senha="Senha@Forte")
    with pytest.raises(SenhaIgualLoginError) as erro:
        controller.adicionar(dados)
    assert str(erro.value) == "Senha: não pode ser igual ao login"
    assert repositorio.listar_todos() == []


def test_deve_validar_politica_antes_da_confirmacao(controller, dados_validos):
    dados = replace(dados_validos, senha="fraca", confirmacao_senha="outra")
    with pytest.raises(SenhaMuitoCurtaError):
        controller.adicionar(dados)
