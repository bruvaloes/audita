from excecao.validacao_error import ValidacaoError


class LoginInvalidoError(ValidacaoError):
    """Base para todos os erros de validação de login.

    Todos exibem a mesma mensagem, que resume a regra completa do login.
    """

    def __init__(self, tamanho_maximo: int):
        super().__init__(
            f"Login: use até {tamanho_maximo} caracteres, sem números"
        )


class LoginVazioError(LoginInvalidoError):
    pass


class LoginMuitoLongoError(LoginInvalidoError):
    pass


class LoginComNumerosError(LoginInvalidoError):
    pass
