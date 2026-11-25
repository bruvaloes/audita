from controle.comando.comando import Comando
from controle.contrato_controller import ContratoController
from entidade.contrato import Contrato
from entidade.usuario import Usuario


class DesfazerUltimaAtualizacaoContratoComando(Comando[Contrato]):
    """Desfaz a última atualização de contrato (editar, encerrar, vincular
    ou desvincular usuário)."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None):
        self._contratos = contratos
        self._solicitante = solicitante

    def executar(self) -> Contrato:
        return self._contratos.desfazer_ultima_atualizacao(self._solicitante)
