from pathlib import Path
from typing import Sequence

from controle.acesso.controle_acesso import ControleAcesso
from controle.acesso.operacao import Operacao
from controle.relatorio.relatorio_acessos import RelatorioAcessos
from entidade.usuario import Usuario
from excecao.validacao_error import FormatoRelatorioInvalidoError


class RelatorioController:
    """Gera os relatórios do sistema para quem tem permissão (RF 15).

    Recebe os formatos do relatório de acessos já montados, sem conhecer
    nenhum deles: cada um é identificado pela própria extensão, e acrescentar
    um formato é uma mudança só na composição, em `main.py`.
    """

    def __init__(self, relatorios_acessos: Sequence[RelatorioAcessos],
                 controle_acesso: ControleAcesso):
        if not relatorios_acessos:
            raise ValueError("Informe ao menos um formato do relatório de acessos.")
        self._relatorios_acessos: dict[str, RelatorioAcessos] = {}
        for relatorio in relatorios_acessos:
            if relatorio.extensao in self._relatorios_acessos:
                raise ValueError(
                    f"Extensão de relatório duplicada: {relatorio.extensao}")
            self._relatorios_acessos[relatorio.extensao] = relatorio
        self._controle_acesso = controle_acesso

    def formatos_relatorio_acessos(self) -> list[str]:
        """Extensões dos formatos disponíveis, na ordem da composição; o
        primeiro é o padrão."""
        return list(self._relatorios_acessos)

    def gerar_relatorio_acessos(self, solicitante: Usuario | None,
                                formato: str | None = None) -> Path:
        """Gera o relatório de acessos no formato pedido (ou no padrão) e
        devolve onde o arquivo foi salvo.

        Levanta AcessoNegadoError se o solicitante não for Gestor (RN15.1),
        FormatoRelatorioInvalidoError se o formato não existir e
        PersistenciaError se não for possível ler os acessos ou gravar.
        """
        self._controle_acesso.verificar(
            solicitante, Operacao.GERAR_RELATORIO_ACESSOS)
        return self._relatorio_do_formato(formato).gerar()

    def _relatorio_do_formato(self, formato: str | None) -> RelatorioAcessos:
        if formato is None:
            return next(iter(self._relatorios_acessos.values()))
        relatorio = self._relatorios_acessos.get(formato.strip().lower())
        if relatorio is None:
            raise FormatoRelatorioInvalidoError(
                ", ".join(self.formatos_relatorio_acessos()))
        return relatorio
