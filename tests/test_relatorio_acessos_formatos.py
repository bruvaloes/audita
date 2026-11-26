"""Issue #119: o relatório em HTML diz o mesmo que o PDF — mesmos rótulos e
números, da mesma fonte (EstatisticasAcessos)."""
from datetime import datetime
from html.parser import HTMLParser

import pytest
from pypdf import PdfReader

from controle.relatorio.relatorio_acessos_html import RelatorioAcessosHtml
from controle.relatorio.relatorio_acessos_pdf import RelatorioAcessosPdf
from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from infraestrutura.acesso_repositorio_memoria import AcessoRepositorioMemoria

GERADO_EM = datetime(2026, 11, 11, 9, 5, 7)


class LeitorDeTexto(HTMLParser):
    """Junta o texto que aparece na página (o `<body>`), uma linha por
    elemento; o `<head>` (título da aba e estilo) fica de fora."""

    def __init__(self):
        super().__init__()
        self.linhas: list[str] = []
        self._no_corpo = False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self._no_corpo = True

    def handle_endtag(self, tag):
        if tag == "body":
            self._no_corpo = False

    def handle_data(self, data):
        if self._no_corpo and data.strip():
            self.linhas.append(data.strip())


def linhas_do_pdf(repositorio, pasta) -> list[str]:
    caminho = RelatorioAcessosPdf(repositorio, pasta_destino=pasta,
                                  relogio=lambda: GERADO_EM).gerar()
    texto = "\n".join(pagina.extract_text()
                      for pagina in PdfReader(caminho).pages)
    return [linha.strip() for linha in texto.splitlines() if linha.strip()]


def linhas_do_html(repositorio, pasta) -> list[str]:
    caminho = RelatorioAcessosHtml(repositorio, pasta_destino=pasta,
                                   relogio=lambda: GERADO_EM).gerar()
    leitor = LeitorDeTexto()
    leitor.feed(caminho.read_text(encoding="utf-8"))
    return leitor.linhas


def com_acessos_variados(repositorio):
    for perfil, resultado, data_hora in (
        (Perfil.GESTOR, ResultadoAcesso.SUCESSO, datetime(2026, 10, 1, 8, 0)),
        (Perfil.FISCAL, ResultadoAcesso.SUCESSO, datetime(2026, 10, 5, 9, 30)),
        (Perfil.FUNCIONARIO, ResultadoAcesso.CREDENCIAIS_INVALIDAS,
         datetime(2026, 10, 20, 17, 15)),
        (None, ResultadoAcesso.CREDENCIAIS_INVALIDAS,
         datetime(2026, 10, 30, 18, 45)),
    ):
        repositorio.salvar(Acesso(0, 1, perfil, data_hora, resultado))
    return repositorio


@pytest.mark.parametrize("repositorio", [
    pytest.param(AcessoRepositorioMemoria(), id="sem-acessos"),
    pytest.param(com_acessos_variados(AcessoRepositorioMemoria()),
                 id="com-acessos"),
])
def test_html_deve_ter_os_mesmos_rotulos_e_numeros_do_pdf(
        repositorio, tmp_path):
    pdf = linhas_do_pdf(repositorio, tmp_path / "pdf")
    html = linhas_do_html(repositorio, tmp_path / "html")

    assert html == pdf
