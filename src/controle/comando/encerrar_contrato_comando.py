from controle.comando.comando import Comando
from controle.contrato_controller import ContratoController
from entidade.contrato import Contrato
from entidade.usuario import Usuario


class EncerrarContratoComando(Comando[Contrato]):
    """Encerra um contrato, mudando a situação para ENCERRADO (RF 06)."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None, numero: str):
        self._contratos = contratos
        self._solicitante = solicitante
        self._numero = numero

    def executar(self) -> Contrato:
        return self._contratos.encerrar(self._solicitante, self._numero)
