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


class TermosNaoAceitosError(ValidacaoError):
    def __init__(self):
        super().__init__(
            "Termos de Uso: aceite os Termos e a Política de Privacidade "
            "para concluir o cadastro"
        )


class DataInvalidaError(ValidacaoError):
    def __init__(self, campo: str):
        super().__init__(f"O campo '{campo}' deve estar no formato dd/mm/aaaa")


class ContratoNumeroJaCadastradoError(ValidacaoError):
    def __init__(self):
        super().__init__("Número de contrato já cadastrado")


class VigenciaInvalidaError(ValidacaoError):
    def __init__(self):
        super().__init__("A data de fim deve ser igual ou posterior à data de início")


class ArquivoInvalidoError(ValidacaoError):
    def __init__(self, mensagem: str = "Arquivo: use PDF ou DOCX com até 30 MB"):
        super().__init__(mensagem)


class PerfilNaoVinculavelError(ValidacaoError):
    def __init__(self):
        super().__init__("Perfil não pode ser vinculado a contrato")


class UltimoFiscalError(ValidacaoError):
    def __init__(self):
        super().__init__("O contrato deve ter ao menos um fiscal")


class ContratoComEvidenciasError(ValidacaoError):
    def __init__(self):
        super().__init__(
            "Contrato com evidências não pode ser removido; encerre-o"
        )


class ContratoNaoEncontradoError(ValidacaoError):
    def __init__(self, mensagem: str = "Contrato não encontrado"):
        super().__init__(mensagem)

