"""Testes unitários dos validadores de senha, isolados do controller."""
import pytest

from controle.validacao.validador_senha import (
    TAMANHO_MAXIMO_SENHA,
    TAMANHO_MINIMO_SENHA,
    ValidadorSenha,
)
from excecao.senha_invalida_error import (
    SenhaComPoucosTiposError,
    SenhaMuitoCurtaError,
    SenhaMuitoLongaError,
)


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
