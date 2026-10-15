from controle.validacao.validador import Validador
from excecao.validacao_error import CampoObrigatorioError


class ValidadorCampoObrigatorio(Validador):

    def __init__(self, nome_campo: str):
        self._nome_campo = nome_campo

    def validar(self, valor: str) -> None:
        if not valor.strip():
            raise CampoObrigatorioError(self._nome_campo)
