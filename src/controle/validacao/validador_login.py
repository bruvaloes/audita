from controle.validacao.validador import Validador
from excecao.login_invalido_error import (
    LoginComNumerosError,
    LoginMuitoLongoError,
    LoginVazioError,
)

TAMANHO_MAXIMO_LOGIN = 12


class ValidadorLogin(Validador):

    def validar(self, valor: str) -> None:
        if not valor.strip():
            raise LoginVazioError()
        if len(valor) > TAMANHO_MAXIMO_LOGIN:
            raise LoginMuitoLongoError(TAMANHO_MAXIMO_LOGIN)
        if any(caractere.isdigit() for caractere in valor):
            raise LoginComNumerosError()
