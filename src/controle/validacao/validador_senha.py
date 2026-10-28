import string

from controle.validacao.validador import Validador
from excecao.senha_invalida_error import (
    SenhaComPoucosTiposError,
    SenhaMuitoCurtaError,
    SenhaMuitoLongaError,
)

TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 128
TIPOS_MINIMOS_SENHA = 3
CARACTERES_ESPECIAIS_SENHA = "!@#$%^&*()_+-=[]{}|'"
TIPOS_DE_CARACTERE = (
    string.ascii_uppercase,
    string.ascii_lowercase,
    string.digits,
    CARACTERES_ESPECIAIS_SENHA,
)
DESCRICAO_POLITICA = (
    f"{TAMANHO_MINIMO_SENHA} a {TAMANHO_MAXIMO_SENHA} caracteres e "
    f"{TIPOS_MINIMOS_SENHA} destes tipos: maiúscula, minúscula, número, "
    f"especial"
)


class ValidadorSenha(Validador):
    """Política de senhas padrão da AWS IAM: 8 a 128 caracteres e pelo
    menos 3 dos 4 tipos de caractere."""

    def validar(self, valor: str) -> None:
        if len(valor) < TAMANHO_MINIMO_SENHA:
            raise SenhaMuitoCurtaError(DESCRICAO_POLITICA)
        if len(valor) > TAMANHO_MAXIMO_SENHA:
            raise SenhaMuitoLongaError(DESCRICAO_POLITICA)
        if self._contar_tipos_presentes(valor) < TIPOS_MINIMOS_SENHA:
            raise SenhaComPoucosTiposError(DESCRICAO_POLITICA)

    @staticmethod
    def _contar_tipos_presentes(texto: str) -> int:
        return sum(
            any(caractere in tipo for caractere in texto)
            for tipo in TIPOS_DE_CARACTERE
        )
