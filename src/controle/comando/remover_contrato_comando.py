from controle.comando.comando import Comando
from controle.comando.dados_comando_contrato import RemocaoContrato
from controle.contrato_controller import ContratoController
from entidade.usuario import Usuario


class RemoverContratoComando(Comando[bool]):
    """Remove um contrato sem evidências após a confirmação (RF 07)."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None, remocao: RemocaoContrato):
        self._contratos = contratos
        self._solicitante = solicitante
        self._remocao = remocao

    def executar(self) -> bool:
        return self._contratos.remover(
            solicitante=self._solicitante,
            numero=self._remocao.numero,
            confirmado=self._remocao.confirmado,
        )
