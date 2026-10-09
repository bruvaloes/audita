class ValidacaoError(Exception):
    """Base para qualquer regra de validação violada no cadastro."""


class CampoObrigatorioError(ValidacaoError):
    def __init__(self, campo: str):
        super().__init__(f"O campo '{campo}' é obrigatório.")


class CpfInvalidoError(ValidacaoError):
    def __init__(self, quantidade_digitos: int):
        super().__init__(
            f"CPF deve conter exatamente {quantidade_digitos} "
            f"dígitos numéricos."
        )


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
        super().__init__(f"Já existe um usuário com este {campo}.")
