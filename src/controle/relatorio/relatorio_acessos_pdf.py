from fpdf import FPDF

from controle.relatorio.estatisticas_acessos import EstatisticasAcessos
from controle.relatorio.relatorio_acessos import (
    ROTULOS_PERFIL,
    ROTULOS_RESULTADO,
    TITULO_RELATORIO,
    RelatorioAcessos,
)
from controle.utils.datas import formatar_data_hora

FONTE = "Helvetica"
TAMANHO_TITULO = 16
TAMANHO_SECAO = 12
TAMANHO_TEXTO = 11
ALTURA_LINHA = 8
RECUO_ITEM = 6


class RelatorioAcessosPdf(RelatorioAcessos):
    """Formato PDF do relatório de acessos (RF 15).

    Só esta classe conhece a biblioteca fpdf2; o passo a passo do relatório
    fica na classe abstrata.
    """

    @property
    def extensao(self) -> str:
        return "pdf"

    def _formatar(self, estatisticas: EstatisticasAcessos) -> bytes:
        pdf = FPDF()
        pdf.set_title(TITULO_RELATORIO)
        pdf.add_page()
        self._escrever_cabecalho(pdf, estatisticas)
        self._escrever_secao(pdf, "Tentativas de login", {
            "Total de tentativas": estatisticas.total,
            "Sucessos": estatisticas.sucessos,
            "Falhas": estatisticas.falhas,
        })
        self._escrever_secao(pdf, "Por resultado", {
            ROTULOS_RESULTADO[resultado]: quantidade
            for resultado, quantidade in estatisticas.por_resultado.items()
        })
        self._escrever_secao(pdf, "Por perfil informado", {
            ROTULOS_PERFIL[perfil]: quantidade
            for perfil, quantidade in estatisticas.por_perfil.items()
        })
        return bytes(pdf.output())

    @staticmethod
    def _escrever_cabecalho(pdf: FPDF, estatisticas: EstatisticasAcessos) -> None:
        pdf.set_font(FONTE, "B", TAMANHO_TITULO)
        pdf.cell(0, ALTURA_LINHA * 1.5, TITULO_RELATORIO,
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(FONTE, "", TAMANHO_TEXTO)
        pdf.cell(0, ALTURA_LINHA,
                 f"Gerado em: {formatar_data_hora(estatisticas.gerado_em)}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, ALTURA_LINHA, f"Período: {_periodo(estatisticas)}",
                 new_x="LMARGIN", new_y="NEXT")

    @staticmethod
    def _escrever_secao(pdf: FPDF, titulo: str,
                        quantidades: dict[str, int]) -> None:
        pdf.ln(ALTURA_LINHA / 2)
        pdf.set_font(FONTE, "B", TAMANHO_SECAO)
        pdf.cell(0, ALTURA_LINHA, titulo, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(FONTE, "", TAMANHO_TEXTO)
        for rotulo, quantidade in quantidades.items():
            pdf.set_x(pdf.l_margin + RECUO_ITEM)
            pdf.cell(0, ALTURA_LINHA, f"{rotulo}: {quantidade}",
                     new_x="LMARGIN", new_y="NEXT")


def _periodo(estatisticas: EstatisticasAcessos) -> str:
    if estatisticas.primeiro_acesso is None:
        return "nenhum acesso registrado"
    return (f"{formatar_data_hora(estatisticas.primeiro_acesso)} a "
            f"{formatar_data_hora(estatisticas.ultimo_acesso)}")
