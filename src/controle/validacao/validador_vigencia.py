from datetime import date

from controle.utils.datas import parsear_data
from excecao.validacao_error import CampoObrigatorioError, VigenciaInvalidaError


class ValidadorVigencia:
    """Valida as datas de início e fim da vigência do contrato (RN04.1 e RN04.2)."""

    def validar(self, vigencia_inicio: str, vigencia_fim: str) -> tuple[date, date]:
        if not vigencia_inicio or not str(vigencia_inicio).strip():
            raise CampoObrigatorioError("Vigência início")

        if not vigencia_fim or not str(vigencia_fim).strip():
            raise CampoObrigatorioError("Vigência fim")

        inicio = parsear_data(vigencia_inicio, "vigência início")
        fim = parsear_data(vigencia_fim, "vigência fim")

        if fim < inicio:
            raise VigenciaInvalidaError()

        return inicio, fim
