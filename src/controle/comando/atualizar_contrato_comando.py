from controle.comando.comando import Comando
from controle.comando.dados_comando_contrato import AtualizacaoContrato
from controle.contrato_controller import ContratoController
from entidade.contrato import Contrato
from entidade.usuario import Usuario


class AtualizarContratoComando(Comando[Contrato]):
    """Atualiza os dados cadastrais de um contrato existente (RF 06)."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None, atualizacao: AtualizacaoContrato):
        self._contratos = contratos
        self._solicitante = solicitante
        self._atualizacao = atualizacao

    def executar(self) -> Contrato:
        return self._contratos.atualizar(
            self._solicitante,
            numero_atual=self._atualizacao.numero_atual,
            dados=self._atualizacao.dados,
        )
