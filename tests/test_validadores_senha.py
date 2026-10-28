"""Testes unitários dos validadores de senha, isolados do controller."""
import pytest

from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.validacao.validador_confirmacao_senha import (
    ValidadorConfirmacaoSenha,
)
from controle.validacao.validador_senha import (
    TAMANHO_MAXIMO_SENHA,
    TAMANHO_MINIMO_SENHA,
    ValidadorSenha,
)
from controle.validacao.validador_senha_diferente_do_login import (
    ValidadorSenhaDiferenteDoLogin,
)
from excecao.senha_invalida_error import (
    SenhaComPoucosTiposError,
    SenhaIgualLoginError,
    SenhaMuitoCurtaError,
    SenhaMuitoLongaError,
    SenhasDiferentesError,
)


def cadastro(login="maria", senha="Senha@123", confirmacao="Senha@123"):
    return DadosCadastroUsuario(
        nome="Maria", cpf="12345678900", email="maria@email.com",
        login=login, senha=senha, confirmacao_senha=confirmacao,
        perfil="GESTOR")


class TestValidadorSenha:

    @pytest.mark.parametrize("senha", [
        "Aa1!bcde", "Abcdefg1", "abcdef1!", "ABCDEF1!", "Abcdefg!",
        "Aa1!" + "b" * (TAMANHO_MAXIMO_SENHA - 4),
    ])
    def test_deve_aceitar_senha_valida(self, senha):
        ValidadorSenha().validar(senha)

    @pytest.mark.parametrize("tamanho", [0, 1, TAMANHO_MINIMO_SENHA - 1])
    def test_deve_rejeitar_senha_curta(self, tamanho):
        with pytest.raises(SenhaMuitoCurtaError):
            ValidadorSenha().validar(("Aa1!" * 3)[:tamanho])

    def test_deve_rejeitar_senha_com_um_caractere_alem_do_maximo(self):
        with pytest.raises(SenhaMuitoLongaError):
            ValidadorSenha().validar("Aa1!" + "b" * (TAMANHO_MAXIMO_SENHA - 3))

    @pytest.mark.parametrize("senha", [
        "abcdefgh", "ABCDEFGH", "12345678", "!@#$%^&*",   # 1 tipo
        "abcdefg1", "ABCDEFG!", "abcdEFGH", "1234567!",   # 2 tipos
    ])
    def test_deve_rejeitar_senha_com_menos_de_3_tipos(self, senha):
        with pytest.raises(SenhaComPoucosTiposError):
            ValidadorSenha().validar(senha)

    def test_letra_acentuada_e_espaco_nao_contam_como_tipo(self):
        with pytest.raises(SenhaComPoucosTiposError):
            ValidadorSenha().validar("áéíóú 12")


class TestValidadorSenhaDiferenteDoLogin:

    def test_deve_aceitar_senha_diferente_do_login(self):
        ValidadorSenhaDiferenteDoLogin().validar(cadastro())

    def test_deve_rejeitar_senha_igual_ao_login(self):
        with pytest.raises(SenhaIgualLoginError):
            ValidadorSenhaDiferenteDoLogin().validar(
                cadastro(login="Senha@Forte", senha="Senha@Forte"))

    def test_deve_diferenciar_maiusculas_de_minusculas(self):
        ValidadorSenhaDiferenteDoLogin().validar(
            cadastro(login="senha@forte", senha="Senha@Forte"))


class TestValidadorConfirmacaoSenha:

    def test_deve_aceitar_confirmacao_igual(self):
        ValidadorConfirmacaoSenha().validar(cadastro())

    @pytest.mark.parametrize("confirmacao", ["", "senha@123", "Senha@1234"])
    def test_deve_rejeitar_confirmacao_diferente(self, confirmacao):
        with pytest.raises(SenhasDiferentesError):
            ValidadorConfirmacaoSenha().validar(
                cadastro(confirmacao=confirmacao))
