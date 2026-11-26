from controle.comando.comando import Comando
from controle.relatorio_controller import RelatorioController


class ListarFormatosRelatorioComando(Comando[list[str]]):
    """Formatos em que o relatório de acessos pode ser gerado; o primeiro é
    o padrão (Issue #119).

    Só lista os nomes dos formatos, sem dado nenhum, e por isso não confere
    permissão: quem gera o relatório continua sendo conferido ao gerar.
    """

    def __init__(self, relatorios: RelatorioController):
        self._relatorios = relatorios

    def executar(self) -> list[str]:
        return self._relatorios.formatos_relatorio_acessos()
