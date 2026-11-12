"""RF 15: esqueleto do relatório de acessos (Template Method) e cálculo das
estatísticas, independentes do formato do arquivo."""
from datetime import datetime

import pytest

from controle.relatorio.estatisticas_acessos import EstatisticasAcessos
from controle.relatorio.relatorio_acessos import RelatorioAcessos
from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from excecao.persistencia_error import (
    EscritaPersistenciaError,
    LeituraPersistenciaError,
)
from infraestrutura.acesso_repositorio_memoria import AcessoRepositorioMemoria
from negocio.acesso_repositorio import ConsultaAcessos

GERADO_EM = datetime(2026, 11, 11, 9, 5, 7)


def acesso(perfil=Perfil.GESTOR, resultado=ResultadoAcesso.SUCESSO,
           data_hora=datetime(2026, 10, 28, 14, 30)) -> Acesso:
    return Acesso(0, 1, perfil, data_hora, resultado)


class RelatorioAcessosTexto(RelatorioAcessos):
    """Formato extra, criado só no teste: um formato novo é uma subclasse,
    sem mudar a classe abstrata nem o PDF (RN15.5)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passos = []

    @property
    def extensao(self) -> str:
        return "txt"

    def _coletar(self):
        self.passos.append("coletar")
        return super()._coletar()

    def _calcular(self, acessos):
        self.passos.append("calcular")
        return super()._calcular(acessos)

    def _formatar(self, estatisticas: EstatisticasAcessos) -> bytes:
        self.passos.append("formatar")
        return (f"total={estatisticas.total};"
                f"sucessos={estatisticas.sucessos};"
                f"falhas={estatisticas.falhas}").encode()

    def _salvar(self, conteudo, gerado_em):
        self.passos.append("salvar")
        return super()._salvar(conteudo, gerado_em)


@pytest.fixture
def repositorio():
    return AcessoRepositorioMemoria()


@pytest.fixture
def relatorio(repositorio, tmp_path):
    return RelatorioAcessosTexto(repositorio, pasta_destino=tmp_path,
                                 relogio=lambda: GERADO_EM)


# --- estatísticas -------------------------------------------------------------

def test_c1_deve_contar_total_sucessos_e_falhas():
    estatisticas = EstatisticasAcessos.calcular([
        acesso(), acesso(),
        acesso(resultado=ResultadoAcesso.CREDENCIAIS_INVALIDAS),
    ], GERADO_EM)

    assert (estatisticas.total, estatisticas.sucessos,
            estatisticas.falhas) == (3, 2, 1)


def test_c2_sem_acessos_deve_zerar_tudo():
    estatisticas = EstatisticasAcessos.calcular([], GERADO_EM)

    assert estatisticas.total == 0
    assert estatisticas.falhas == 0
    assert set(estatisticas.por_resultado.values()) == {0}
    assert set(estatisticas.por_perfil.values()) == {0}
    assert estatisticas.primeiro_acesso is None
    assert estatisticas.ultimo_acesso is None


def test_deve_contar_por_resultado_inclusive_bloqueado_zerado():
    estatisticas = EstatisticasAcessos.calcular([
        acesso(), acesso(resultado=ResultadoAcesso.CREDENCIAIS_INVALIDAS),
    ], GERADO_EM)

    assert estatisticas.por_resultado == {
        ResultadoAcesso.SUCESSO: 1,
        ResultadoAcesso.CREDENCIAIS_INVALIDAS: 1,
        ResultadoAcesso.BLOQUEADO: 0,
    }


def test_deve_contar_por_perfil_informado_e_perfil_invalido():
    estatisticas = EstatisticasAcessos.calcular([
        acesso(Perfil.GESTOR), acesso(Perfil.FUNCIONARIO),
        acesso(Perfil.FUNCIONARIO), acesso(None),
    ], GERADO_EM)

    assert estatisticas.por_perfil == {
        Perfil.GESTOR: 1, Perfil.FISCAL: 0, Perfil.FUNCIONARIO: 2, None: 1,
    }


def test_deve_guardar_o_periodo_dos_acessos_e_a_data_de_geracao():
    primeiro = datetime(2026, 10, 1, 8, 0)
    ultimo = datetime(2026, 10, 30, 18, 45)
    estatisticas = EstatisticasAcessos.calcular(
        [acesso(data_hora=ultimo), acesso(data_hora=primeiro)], GERADO_EM)

    assert estatisticas.primeiro_acesso == primeiro
    assert estatisticas.ultimo_acesso == ultimo
    assert estatisticas.gerado_em == GERADO_EM


# --- Template Method ------------------------------------------------------------

def test_gerar_deve_seguir_os_passos_na_ordem(relatorio):
    relatorio.gerar()

    assert relatorio.passos == ["coletar", "calcular", "formatar", "salvar"]


def test_deve_usar_os_acessos_gravados_no_login(relatorio, repositorio):
    for resultado in (ResultadoAcesso.SUCESSO, ResultadoAcesso.SUCESSO,
                      ResultadoAcesso.CREDENCIAIS_INVALIDAS):
        repositorio.salvar(acesso(resultado=resultado))

    caminho = relatorio.gerar()

    assert caminho.read_bytes() == b"total=3;sucessos=2;falhas=1"


def test_deve_salvar_na_pasta_com_data_brasileira_e_extensao_do_formato(
        relatorio, tmp_path):
    caminho = relatorio.gerar()

    assert caminho.parent == tmp_path.resolve()
    assert caminho.name == "relatorio-acessos_11-11-2026_09-05-07.txt"
    assert caminho.is_absolute()


def test_deve_criar_a_pasta_de_destino_se_nao_existir(repositorio, tmp_path):
    pasta = tmp_path / "relatorios" / "acessos"
    relatorio = RelatorioAcessosTexto(repositorio, pasta_destino=pasta,
                                      relogio=lambda: GERADO_EM)

    assert relatorio.gerar().exists()


def test_falha_ao_gravar_deve_virar_erro_de_persistencia(repositorio, tmp_path):
    arquivo_no_lugar_da_pasta = tmp_path / "ocupado"
    arquivo_no_lugar_da_pasta.write_text("")
    relatorio = RelatorioAcessosTexto(
        repositorio, pasta_destino=arquivo_no_lugar_da_pasta,
        relogio=lambda: GERADO_EM)

    with pytest.raises(EscritaPersistenciaError, match="relatório"):
        relatorio.gerar()


def test_falha_ao_ler_os_acessos_deve_subir_sem_gerar_arquivo(tmp_path):
    class ConsultaQueFalha(ConsultaAcessos):
        def listar_todos(self):
            raise LeituraPersistenciaError("banco indisponível")

    relatorio = RelatorioAcessosTexto(ConsultaQueFalha(),
                                      pasta_destino=tmp_path)

    with pytest.raises(LeituraPersistenciaError):
        relatorio.gerar()
    assert list(tmp_path.iterdir()) == []


def test_formato_sem_formatar_nao_pode_ser_instanciado(repositorio):
    class FormatoIncompleto(RelatorioAcessos):
        extensao = "x"

    with pytest.raises(TypeError):
        FormatoIncompleto(repositorio)
