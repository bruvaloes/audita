from excecao.validacao_error import ValidacaoError


class SenhaInvalidaError(ValidacaoError):
    """Base para todos os erros de validação de senha."""


class SenhaForaDaPoliticaError(SenhaInvalidaError):
    """Base dos erros de tamanho e variedade de caracteres da senha.

    Todos exibem a mesma mensagem, que resume a política completa.
    """

    def __init__(self, descricao_politica: str):
        super().__init__(f"Senha: use {descricao_politica}")


class SenhaMuitoCurtaError(SenhaForaDaPoliticaError):
    pass


class SenhaMuitoLongaError(SenhaForaDaPoliticaError):
    pass


class SenhaComPoucosTiposError(SenhaForaDaPoliticaError):
    pass


class SenhasDiferentesError(SenhaInvalidaError):
    def __init__(self):
        super().__init__("As senhas não coincidem")
