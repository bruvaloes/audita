class ValidacaoError(Exception):
    """Base para qualquer regra de validação violada no cadastro."""


class CampoObrigatorioError(ValidacaoError):
    def __init__(self, campo: str):
        super().__init__(f"O campo '{campo}' é obrigatório.")


class CpfInvalidoError(ValidacaoError):
    def __init__(self):
        super().__init__("CPF inválido")


class EmailInvalidoError(ValidacaoError):
    def __init__(self):
        super().__init__("E-mail deve conter '@'.")


class PerfilInvalidoError(ValidacaoError):
    def __init__(self, perfil: str, valores_aceitos: str):
        super().__init__(
            f"Perfil inválido: '{perfil}'. Valores aceitos: {valores_aceitos}."
        )


class UsuarioDuplicadoError(ValidacaoError):
    def __init__(self, campo: str):
        super().__init__(f"{campo} já cadastrado")
