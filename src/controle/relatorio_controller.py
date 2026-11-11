from pathlib import Path

from controle.acesso.controle_acesso import ControleAcesso
from controle.acesso.operacao import Operacao
from controle.relatorio.relatorio_acessos import RelatorioAcessos
from entidade.usuario import Usuario


class RelatorioController:
    """Gera os relatórios do sistema para quem tem permissão (RF 15).

    Recebe o relatório pronto para gerar, sem saber o formato: trocar o PDF
    por outro formato é uma mudança só na composição, em `main.py`.
    """

    def __init__(self, relatorio_acessos: RelatorioAcessos,
                 controle_acesso: ControleAcesso):
        self._relatorio_acessos = relatorio_acessos
        self._controle_acesso = controle_acesso

    def gerar_relatorio_acessos(self, solicitante: Usuario | None) -> Path:
        """Gera o relatório de acessos e devolve onde o arquivo foi salvo.

        Levanta AcessoNegadoError se o solicitante não for Gestor (RN15.1)
        e PersistenciaError se não for possível ler os acessos ou gravar.
        """
        self._controle_acesso.verificar(
            solicitante, Operacao.GERAR_RELATORIO_ACESSOS)
        return self._relatorio_acessos.gerar()
