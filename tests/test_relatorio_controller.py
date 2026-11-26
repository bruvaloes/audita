"""RF 15: só o Gestor gera o relatório de acessos, e a permissão é conferida
no controller (RN15.1, C3). O controller escolhe o formato pela extensão
(Issue #119)."""
from unittest.mock import MagicMock

import pytest

from controle.relatorio.relatorio_acessos import RelatorioAcessos
from controle.relatorio.relatorio_acessos_pdf import RelatorioAcessosPdf
from controle.relatorio_controller import RelatorioController
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.acesso_negado_error import AcessoNegadoError
from excecao.validacao_error import FormatoRelatorioInvalidoError


def usuario_com(perfil: Perfil) -> Usuario:
    return Usuario(1, "Ana", "52998224725", "ana@email.com", "ana", "hash",
                   perfil)


def relatorio_no_formato(extensao: str):
    relatorio = MagicMock(spec=RelatorioAcessos)
    relatorio.extensao = extensao
    return relatorio


@pytest.fixture
def relatorio():
    return relatorio_no_formato("pdf")


@pytest.fixture
def outro_formato():
    return relatorio_no_formato("html")


@pytest.fixture
def relatorio_controller(relatorio, outro_formato, controle_acesso):
    return RelatorioController([relatorio, outro_formato], controle_acesso)


def test_gestor_deve_gerar_o_relatorio(relatorio_controller, relatorio,
                                       tmp_path):
    relatorio.gerar.return_value = tmp_path / "relatorio.pdf"

    caminho = relatorio_controller.gerar_relatorio_acessos(
        usuario_com(Perfil.GESTOR))

    assert caminho == tmp_path / "relatorio.pdf"
    relatorio.gerar.assert_called_once_with()


def test_sem_formato_deve_gerar_no_primeiro_da_composicao(
        relatorio_controller, relatorio, outro_formato):
    relatorio_controller.gerar_relatorio_acessos(usuario_com(Perfil.GESTOR))

    relatorio.gerar.assert_called_once_with()
    outro_formato.gerar.assert_not_called()


@pytest.mark.parametrize("formato", ["html", " HTML "])
def test_deve_gerar_no_formato_pedido(
        relatorio_controller, relatorio, outro_formato, formato):
    relatorio_controller.gerar_relatorio_acessos(
        usuario_com(Perfil.GESTOR), formato)

    outro_formato.gerar.assert_called_once_with()
    relatorio.gerar.assert_not_called()


def test_formato_desconhecido_deve_listar_os_aceitos(
        relatorio_controller, relatorio, outro_formato):
    with pytest.raises(FormatoRelatorioInvalidoError,
                       match="use um destes valores: pdf, html"):
        relatorio_controller.gerar_relatorio_acessos(
            usuario_com(Perfil.GESTOR), "docx")

    relatorio.gerar.assert_not_called()
    outro_formato.gerar.assert_not_called()


def test_deve_listar_os_formatos_na_ordem_da_composicao(relatorio_controller):
    assert relatorio_controller.formatos_relatorio_acessos() == ["pdf", "html"]


def test_sem_nenhum_formato_nao_deve_ser_criado(controle_acesso):
    with pytest.raises(ValueError):
        RelatorioController([], controle_acesso)


@pytest.mark.parametrize("perfil", [Perfil.FISCAL, Perfil.FUNCIONARIO])
def test_c3_outros_perfis_devem_receber_acesso_negado(
        relatorio_controller, relatorio, perfil):
    with pytest.raises(AcessoNegadoError, match="Acesso negado"):
        relatorio_controller.gerar_relatorio_acessos(usuario_com(perfil))

    relatorio.gerar.assert_not_called()


def test_permissao_deve_ser_conferida_antes_do_formato(relatorio_controller):
    with pytest.raises(AcessoNegadoError):
        relatorio_controller.gerar_relatorio_acessos(
            usuario_com(Perfil.FISCAL), "docx")


def test_sem_usuario_autenticado_deve_negar(relatorio_controller, relatorio):
    with pytest.raises(AcessoNegadoError):
        relatorio_controller.gerar_relatorio_acessos(None)

    relatorio.gerar.assert_not_called()


def test_c3_perfil_negado_nao_deve_criar_arquivo(
        acessos, controle_acesso, tmp_path):
    controller = RelatorioController(
        [RelatorioAcessosPdf(acessos, pasta_destino=tmp_path / "relatorios")],
        controle_acesso)

    with pytest.raises(AcessoNegadoError):
        controller.gerar_relatorio_acessos(usuario_com(Perfil.FUNCIONARIO))

    assert not (tmp_path / "relatorios").exists()
