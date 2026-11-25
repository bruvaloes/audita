from controle.comando.comando import Comando
from controle.comando.dados_comando_contrato import VinculoContrato
from controle.contrato_controller import ContratoController
from entidade.usuario import Usuario


class VincularUsuarioContratoComando(Comando[None]):
    """Vincula um fiscal ou funcionário a um contrato (RF 08)."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None, vinculo: VinculoContrato):
        self._contratos = contratos
        self._solicitante = solicitante
        self._vinculo = vinculo

    def executar(self) -> None:
        self._contratos.vincular(
            solicitante=self._solicitante,
            numero=self._vinculo.numero,
            id_usuario=self._vinculo.id_usuario,
        )
