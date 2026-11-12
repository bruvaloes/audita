"""RF 15: relatório de acessos em PDF, com datas no padrão brasileiro
(NF006 de Adequação)."""
import re
from datetime import datetime

import pytest
from pypdf import PdfReader

from controle.relatorio.relatorio_acessos_pdf import RelatorioAcessosPdf
from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from infraestrutura.acesso_repositorio_memoria import AcessoRepositorioMemoria
from infraestrutura.acesso_repositorio_sqlite import AcessoRepositorioSQLite

GERADO_EM = datetime(2026, 11, 11, 9, 5, 7)
DATA_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


@pytest.fixture
def repositorio():
    return AcessoRepositorioMemoria()


def registrar(repositorio, perfil, resultado,
              data_hora=datetime(2026, 10, 28, 14, 30, 5)) -> None:
    repositorio.salvar(Acesso(0, 1, perfil, data_hora, resultado))


def gerar_e_ler(repositorio, tmp_path) -> str:
    relatorio = RelatorioAcessosPdf(repositorio, pasta_destino=tmp_path,
                                    relogio=lambda: GERADO_EM)
    caminho = relatorio.gerar()
    return "\n".join(pagina.extract_text()
                     for pagina in PdfReader(caminho).pages)


def test_deve_gerar_um_arquivo_pdf(repositorio, tmp_path):
    caminho = RelatorioAcessosPdf(repositorio, pasta_destino=tmp_path).gerar()

    assert caminho.suffix == ".pdf"
    assert caminho.read_bytes().startswith(b"%PDF-")


def test_c1_deve_mostrar_total_3_com_2_sucessos_e_1_falha(
        repositorio, tmp_path):
    registrar(repositorio, Perfil.GESTOR, ResultadoAcesso.SUCESSO)
    registrar(repositorio, Perfil.FUNCIONARIO, ResultadoAcesso.SUCESSO)
    registrar(repositorio, Perfil.FISCAL,
              ResultadoAcesso.CREDENCIAIS_INVALIDAS)

    texto = gerar_e_ler(repositorio, tmp_path)

    assert "Total de tentativas: 3" in texto
    assert "Sucessos: 2" in texto
    assert "Falhas: 1" in texto
    assert "Credenciais inválidas: 1" in texto


def test_c2_sem_acessos_deve_mostrar_total_0(repositorio, tmp_path):
    texto = gerar_e_ler(repositorio, tmp_path)

    assert "Total de tentativas: 0" in texto
    assert "Período: nenhum acesso registrado" in texto


def test_deve_mostrar_bloqueado_mesmo_com_zero(repositorio, tmp_path):
    registrar(repositorio, Perfil.GESTOR, ResultadoAcesso.SUCESSO)

    assert "Bloqueado: 0" in gerar_e_ler(repositorio, tmp_path)


def test_deve_mostrar_a_quantidade_por_perfil_informado(
        repositorio, tmp_path):
    registrar(repositorio, Perfil.FUNCIONARIO, ResultadoAcesso.SUCESSO)
    registrar(repositorio, Perfil.FUNCIONARIO, ResultadoAcesso.SUCESSO)
    registrar(repositorio, None, ResultadoAcesso.CREDENCIAIS_INVALIDAS)

    texto = gerar_e_ler(repositorio, tmp_path)

    assert "Funcionário: 2" in texto
    assert "Gestor: 0" in texto
    assert "Fiscal: 0" in texto
    assert "Perfil inválido: 1" in texto


def test_datas_devem_estar_em_dd_mm_aaaa_hh_mm(repositorio, tmp_path):
    registrar(repositorio, Perfil.GESTOR, ResultadoAcesso.SUCESSO,
              datetime(2026, 10, 1, 8, 0, 59))
    registrar(repositorio, Perfil.GESTOR, ResultadoAcesso.SUCESSO,
              datetime(2026, 10, 30, 18, 45, 12))

    texto = gerar_e_ler(repositorio, tmp_path)

    assert "Gerado em: 11/11/2026 09:05" in texto
    assert "Período: 01/10/2026 08:00 a 30/10/2026 18:45" in texto


def test_nenhuma_data_deve_aparecer_em_formato_iso(repositorio, tmp_path):
    registrar(repositorio, Perfil.GESTOR, ResultadoAcesso.SUCESSO,
              datetime(2026, 10, 1, 8, 0, 59))
    registrar(repositorio, Perfil.GESTOR, ResultadoAcesso.SUCESSO,
              datetime(2026, 10, 30, 18, 45, 12))

    texto = gerar_e_ler(repositorio, tmp_path)

    assert not DATA_ISO.search(texto)
    assert "T08:00" not in texto
    assert ":59" not in texto and ":12" not in texto  # sem segundos


def test_deve_ler_os_acessos_gravados_no_sqlite(tmp_path):
    repositorio = AcessoRepositorioSQLite(str(tmp_path / "usuarios.db"))
    registrar(repositorio, Perfil.GESTOR, ResultadoAcesso.SUCESSO)
    registrar(repositorio, Perfil.GESTOR,
              ResultadoAcesso.CREDENCIAIS_INVALIDAS)

    texto = gerar_e_ler(repositorio, tmp_path)

    assert "Total de tentativas: 2" in texto
    assert "Período: 28/10/2026 14:30 a 28/10/2026 14:30" in texto
