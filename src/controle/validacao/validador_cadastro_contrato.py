from datetime import date

from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.validacao.validador_arquivo_contrato import ValidadorArquivoContrato
from controle.validacao.validador_empresa_contratada import ValidadorEmpresaContratada
from controle.validacao.validador_numero_contrato import ValidadorNumeroContrato
from controle.validacao.validador_vigencia import ValidadorVigencia
from persistencia.contrato_repositorio import ConsultaContratos


class ValidadorCadastroContrato:
    """Validador composto para cadastro e edição de contrato (RF 04 e RF 06)."""

    def __init__(
        self,
        consulta: ConsultaContratos | None = None,
        permitir_numero: str | None = None,
    ):
        self._validador_numero = ValidadorNumeroContrato(consulta, permitir_numero)
        self._validador_empresa = ValidadorEmpresaContratada()
        self._validador_vigencia = ValidadorVigencia()
        self._validador_arquivo = ValidadorArquivoContrato()

    def validar(self, dados: DadosCadastroContrato) -> tuple[date, date]:
        """Aplica todas as validações aos dados do contrato.

        Retorna as datas de início e fim da vigência convertidas.
        """
        self._validador_numero.validar(dados.numero)
        self._validador_empresa.validar(dados.empresa_contratada)
        inicio, fim = self._validador_vigencia.validar(
            dados.vigencia_inicio, dados.vigencia_fim
        )
        self._validador_arquivo.validar(dados.arquivo)
        return inicio, fim
