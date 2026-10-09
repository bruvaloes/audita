from controle.validacao.validador import Validador
from excecao.validacao_error import EmailInvalidoError

SEPARADOR_EMAIL = "@"


class ValidadorEmail(Validador):

    def validar(self, valor: str) -> None:
        if SEPARADOR_EMAIL not in valor:
            raise EmailInvalidoError()
