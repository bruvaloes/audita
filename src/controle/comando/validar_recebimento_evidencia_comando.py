from controle.comando.comando import Comando
from controle.contrato_controller import ContratoController


class ValidarRecebimentoEvidenciaComando(Comando[None]):
    """Confere se o contrato está ativo para receber evidências (RN06.2)."""

    def __init__(self, contratos: ContratoController, numero: str):
        self._contratos = contratos
        self._numero = numero

    def executar(self) -> None:
        self._contratos.validar_recebimento_evidencia(self._numero)
