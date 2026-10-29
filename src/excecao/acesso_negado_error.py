MENSAGEM_ACESSO_NEGADO = "Acesso negado"


class AcessoNegadoError(Exception):
    """O usuário (ou a falta dele) não tem permissão para a operação (RF 03).

    Não herda de ValidacaoError: não é um dado inválido, e a mensagem não
    revela quais perfis teriam acesso.
    """

    def __init__(self):
        super().__init__(MENSAGEM_ACESSO_NEGADO)
