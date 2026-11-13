from controle.comando.comando import Comando
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.contrato import Contrato
from entidade.usuario import Usuario


class CadastrarContratoComando(Comando[Contrato]):
    """Cadastra um novo contrato ativo (RF 04)."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None, dados: DadosCadastroContrato):
        self._contratos = contratos
        self._solicitante = solicitante
        self._dados = dados

    def executar(self) -> Contrato:
        return self._contratos.adicionar(self._solicitante, self._dados)
