from controle.comando.comando import Comando
from controle.contrato_controller import ContratoController
from entidade.contrato import Contrato
from entidade.usuario import Usuario


class BuscarContratoComando(Comando[Contrato | None]):
    """Busca um contrato pelo seu número."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None, numero: str):
        self._contratos = contratos
        self._solicitante = solicitante
        self._numero = numero

    def executar(self) -> Contrato | None:
        return self._contratos.buscar_por_numero(
            self._solicitante, self._numero)
