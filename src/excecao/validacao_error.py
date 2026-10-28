class ValidacaoError(Exception):
    """Base para qualquer regra de validação violada no cadastro."""


class CampoObrigatorioError(ValidacaoError):
    def __init__(self, campo: str):
        super().__init__(f"O campo '{campo}' é obrigatório.")


class CpfInvalidoError(ValidacaoError):
    def __init__(self):
        super().__init__("CPF inválido")


class NomeMuitoLongoError(ValidacaoError):
    def __init__(self, tamanho_maximo: int):
        super().__init__(f"Nome: use até {tamanho_maximo} caracteres")


class EmailInvalidoError(ValidacaoError):
    def __init__(self, tamanho_maximo: int):
        super().__init__(
            f"E-mail: use o formato nome@dominio, com até "
            f"{tamanho_maximo} caracteres"
        )


class PerfilInvalidoError(ValidacaoError):
    def __init__(self, valores_aceitos: str):
        super().__init__(f"Perfil: use um destes valores: {valores_aceitos}")


class UsuarioDuplicadoError(ValidacaoError):
    def __init__(self, campo: str):
        super().__init__(f"{campo} já cadastrado")
