from controle.validacao.validador import Validador
from excecao.validacao_error import NomeMuitoLongoError

TAMANHO_MAXIMO_NOME = 100


class ValidadorNome(Validador):

    def validar(self, valor: str) -> None:
        if len(valor.strip()) > TAMANHO_MAXIMO_NOME:
            raise NomeMuitoLongoError(TAMANHO_MAXIMO_NOME)
