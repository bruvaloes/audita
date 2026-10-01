class LoginInvalidoError(Exception):
    """Base para todos os erros de validação de login."""


class LoginVazioError(LoginInvalidoError):
    def __init__(self):
        super().__init__("O login não pode ser vazio.")


class LoginMuitoLongoError(LoginInvalidoError):
    def __init__(self, tamanho_maximo: int):
        super().__init__(
            f"O login deve ter no máximo {tamanho_maximo} caracteres."
        )


class LoginComNumerosError(LoginInvalidoError):
    def __init__(self):
        super().__init__("O login não pode conter números.")
