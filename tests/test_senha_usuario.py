import pytest

from controle.usuario_controller import UsuarioController
from entidade.perfil import Perfil
from excecao.senha_invalida_error import (
    SenhaInvalidaError,
    SenhaMuitoCurtaError,
    SenhaMuitoLongaError,
    SenhaSemCaractereEspecialError,
    SenhaSemMaiusculaError,
    SenhaSemMinusculaError,
    SenhaSemNumeroError,
)
from persistencia.usuario_repositorio import UsuarioRepositorioMemoria

TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 128
CARACTERES_ESPECIAIS_SENHA = "!@#$%^&*()_+-=[]{}|'"

@pytest.fixture
def controller():
    return UsuarioController(UsuarioRepositorioMemoria())


def adicionar(controller, senha):
    return controller.adicionar(
        "Maria", "12345678900", "maria@email.com", "maria", senha,
        next(iter(Perfil)).value
    )


@pytest.mark.parametrize("senha", ["Senha@123", "P4ssw0rd!", "A1#bcdefgh", "Senh4_F0rt3("])
def test_deve_aceitar_senha_valida(controller, senha):
    assert adicionar(controller, senha).senha == senha


@pytest.mark.parametrize("senha", ["1@Abcde", "S@1abcd"])  # 7 caracteres
def test_deve_lancar_erro_quando_senha_muito_curta(controller, senha):
    with pytest.raises(SenhaMuitoCurtaError):
        adicionar(controller, senha)


def test_deve_lancar_erro_quando_senha_muito_longa(controller):
    with pytest.raises(SenhaMuitoLongaError):
        # Cria uma senha com 129 caracteres (1 caractere a mais que o máximo permitido)
        senha_longa = "S@1a" + ("b" * (TAMANHO_MAXIMO_SENHA - 3))
        adicionar(controller, senha_longa)


@pytest.mark.parametrize("senha", ["senha@1234", "minha_senha1"])
def test_deve_lancar_erro_quando_senha_sem_maiuscula(controller, senha):
    with pytest.raises(SenhaSemMaiusculaError):
        adicionar(controller, senha)


@pytest.mark.parametrize("senha", ["SENHA@1234", "MINHA_SENHA1"])
def test_deve_lancar_erro_quando_senha_sem_minuscula(controller, senha):
    with pytest.raises(SenhaSemMinusculaError):
        adicionar(controller, senha)


@pytest.mark.parametrize("senha", ["Senha@Forte", "Outra$Senha"])
def test_deve_lancar_erro_quando_senha_sem_numero(controller, senha):
    with pytest.raises(SenhaSemNumeroError):
        adicionar(controller, senha)


@pytest.mark.parametrize("senha", ["Senha12345", "S3nhaForte"])
def test_deve_lancar_erro_quando_senha_sem_caractere_especial(controller, senha):
    with pytest.raises(SenhaSemCaractereEspecialError):
        adicionar(controller, senha)


def test_erros_de_senha_herdam_de_senha_invalida_error(controller):
    with pytest.raises(SenhaInvalidaError):
        adicionar(controller, "fraca")

def test_nao_deve_salvar_usuario_quando_senha_invalida(controller):
    with pytest.raises(SenhaInvalidaError):
        adicionar(controller, "fraca")
    assert controller.listar_todos() == []