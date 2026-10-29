from controle.validacao.validador import Validador
from excecao.validacao_error import (
    CampoObrigatorioError,
    ContratoNumeroJaCadastradoError,
    ValidacaoError,
)
from persistencia.contrato_repositorio import ConsultaContratos


class ValidadorNumeroContrato(Validador):
    """Valida o número do contrato: obrigatório, até 20 caracteres e único (RN04.1)."""

    def __init__(
        self,
        consulta: ConsultaContratos | None = None,
        permitir_numero: str | None = None,
    ):
        self._consulta = consulta
        self._permitir_numero = permitir_numero

    def validar(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise CampoObrigatorioError("Número do contrato")

        limpo = valor.strip()
        if len(limpo) > 20:
            raise ValidacaoError("Número do contrato: use até 20 caracteres")

        if self._consulta is not None:
            if self._permitir_numero and limpo == self._permitir_numero:
                return
            if self._consulta.buscar_por_numero(limpo) is not None:
                raise ContratoNumeroJaCadastradoError()
