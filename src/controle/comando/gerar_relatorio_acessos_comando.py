from pathlib import Path

from controle.comando.comando import Comando
from controle.relatorio_controller import RelatorioController
from entidade.usuario import Usuario


class GerarRelatorioAcessosComando(Comando[Path]):
    """Gera o relatório de estatísticas de acesso e devolve onde o arquivo
    foi salvo (RF 15)."""

    def __init__(self, relatorios: RelatorioController,
                 solicitante: Usuario | None):
        self._relatorios = relatorios
        self._solicitante = solicitante

    def executar(self) -> Path:
        return self._relatorios.gerar_relatorio_acessos(self._solicitante)
