from controle.validacao.validador import Validador
from excecao.validacao_error import CpfInvalidoError

QUANTIDADE_DIGITOS_CPF = 11


class ValidadorCpf(Validador):

    def validar(self, valor: str) -> None:
        digitos = valor.replace(".", "").replace("-", "")
        if not digitos.isdigit() or len(digitos) != QUANTIDADE_DIGITOS_CPF:
            raise CpfInvalidoError(QUANTIDADE_DIGITOS_CPF)
