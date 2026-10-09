import string

from controle.validacao.validador import Validador
from excecao.senha_invalida_error import (
    SenhaMuitoCurtaError,
    SenhaMuitoLongaError,
    SenhaSemCaractereEspecialError,
    SenhaSemMaiusculaError,
    SenhaSemMinusculaError,
    SenhaSemNumeroError,
)

TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 128
CARACTERES_ESPECIAIS_SENHA = "!@#$%^&*()_+-=[]{}|'"


class ValidadorSenha(Validador):
    """Política de senhas inspirada na do AWS IAM."""

    def validar(self, valor: str) -> None:
        if len(valor) < TAMANHO_MINIMO_SENHA:
            raise SenhaMuitoCurtaError(TAMANHO_MINIMO_SENHA)
        if len(valor) > TAMANHO_MAXIMO_SENHA:
            raise SenhaMuitoLongaError(TAMANHO_MAXIMO_SENHA)
        if not self._contem_algum_de(valor, string.ascii_uppercase):
            raise SenhaSemMaiusculaError()
        if not self._contem_algum_de(valor, string.ascii_lowercase):
            raise SenhaSemMinusculaError()
        if not self._contem_algum_de(valor, string.digits):
            raise SenhaSemNumeroError()
        if not self._contem_algum_de(valor, CARACTERES_ESPECIAIS_SENHA):
            raise SenhaSemCaractereEspecialError(CARACTERES_ESPECIAIS_SENHA)

    @staticmethod
    def _contem_algum_de(texto: str, caracteres: str) -> bool:
        return any(caractere in caracteres for caractere in texto)
