from excecao.validacao_error import ValidacaoError


class SenhaInvalidaError(ValidacaoError):
    """Base para todos os erros de validação de senha."""


class SenhaMuitoCurtaError(SenhaInvalidaError):
    def __init__(self, tamanho_minimo: int):
        super().__init__(
            f"A senha deve ter no mínimo {tamanho_minimo} caracteres."
        )


class SenhaMuitoLongaError(SenhaInvalidaError):
    def __init__(self, tamanho_maximo: int):
        super().__init__(
            f"A senha deve ter no máximo {tamanho_maximo} caracteres."
        )


class SenhaSemMaiusculaError(SenhaInvalidaError):
    def __init__(self):
        super().__init__(
            "A senha deve conter pelo menos uma letra maiúscula (A-Z)."
        )


class SenhaSemMinusculaError(SenhaInvalidaError):
    def __init__(self):
        super().__init__(
            "A senha deve conter pelo menos uma letra minúscula (a-z)."
        )


class SenhaSemNumeroError(SenhaInvalidaError):
    def __init__(self):
        super().__init__(
            "A senha deve conter pelo menos um número (0-9)."
        )


class SenhaSemCaractereEspecialError(SenhaInvalidaError):
    def __init__(self, caracteres_aceitos: str):
        super().__init__(
            f"A senha deve conter pelo menos um caractere especial "
            f"({caracteres_aceitos})."
        )
