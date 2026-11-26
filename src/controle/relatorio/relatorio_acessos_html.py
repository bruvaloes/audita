from html import escape

from controle.relatorio.estatisticas_acessos import EstatisticasAcessos
from controle.relatorio.relatorio_acessos import (
    ROTULOS_PERFIL,
    ROTULOS_RESULTADO,
    TITULO_RELATORIO,
    RelatorioAcessos,
)
from controle.utils.datas import formatar_data_hora

CODIFICACAO = "utf-8"
ESTILO = (
    "body { font-family: Helvetica, Arial, sans-serif; margin: 2rem; }"
    " h1 { font-size: 1.6rem; } h2 { font-size: 1.2rem; margin-top: 1.5rem; }"
    " ul { list-style: none; padding-left: 1.5rem; } li { margin: 0.3rem 0; }"
)


class RelatorioAcessosHtml(RelatorioAcessos):
    """Formato HTML do relatório de acessos (RF 15, Issue #119).

    Segunda subclasse do Template Method: só define a extensão e a
    formatação; coletar, calcular e salvar vêm da classe abstrata. Traz as
    mesmas seções, rótulos e números do PDF, numa página para abrir no
    navegador.
    """

    @property
    def extensao(self) -> str:
        return "html"

    def _formatar(self, estatisticas: EstatisticasAcessos) -> bytes:
        partes = [
            "<!DOCTYPE html>",
            '<html lang="pt-BR">',
            "<head>",
            f'<meta charset="{CODIFICACAO}">',
            f"<title>{escape(TITULO_RELATORIO)}</title>",
            f"<style>{ESTILO}</style>",
            "</head>",
            "<body>",
            *self._cabecalho(estatisticas),
            *self._secao("Tentativas de login", {
                "Total de tentativas": estatisticas.total,
                "Sucessos": estatisticas.sucessos,
                "Falhas": estatisticas.falhas,
            }),
            *self._secao("Por resultado", {
                ROTULOS_RESULTADO[resultado]: quantidade
                for resultado, quantidade in estatisticas.por_resultado.items()
            }),
            *self._secao("Por perfil informado", {
                ROTULOS_PERFIL[perfil]: quantidade
                for perfil, quantidade in estatisticas.por_perfil.items()
            }),
            "</body>",
            "</html>",
        ]
        return ("\n".join(partes) + "\n").encode(CODIFICACAO)

    @staticmethod
    def _cabecalho(estatisticas: EstatisticasAcessos) -> list[str]:
        gerado_em = formatar_data_hora(estatisticas.gerado_em)
        return [
            f"<h1>{escape(TITULO_RELATORIO)}</h1>",
            f"<p>Gerado em: {escape(gerado_em)}</p>",
            f"<p>Período: {escape(_periodo(estatisticas))}</p>",
        ]

    @staticmethod
    def _secao(titulo: str, quantidades: dict[str, int]) -> list[str]:
        itens = [f"<li>{escape(rotulo)}: {quantidade}</li>"
                 for rotulo, quantidade in quantidades.items()]
        return [f"<h2>{escape(titulo)}</h2>", "<ul>", *itens, "</ul>"]


def _periodo(estatisticas: EstatisticasAcessos) -> str:
    if estatisticas.primeiro_acesso is None:
        return "nenhum acesso registrado"
    return (f"{formatar_data_hora(estatisticas.primeiro_acesso)} a "
            f"{formatar_data_hora(estatisticas.ultimo_acesso)}")
