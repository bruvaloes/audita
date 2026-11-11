"""RF 15: só o Gestor gera o relatório de acessos, e a permissão é conferida
no controller (RN15.1, C3)."""
from unittest.mock import MagicMock

import pytest

from controle.relatorio.relatorio_acessos import RelatorioAcessos
from controle.relatorio.relatorio_acessos_pdf import RelatorioAcessosPdf
from controle.relatorio_controller import RelatorioController
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.acesso_negado_error import AcessoNegadoError


def usuario_com(perfil: Perfil) -> Usuario:
    return Usuario(1, "Ana", "52998224725", "ana@email.com", "ana", "hash",
                   perfil)


@pytest.fixture
def relatorio():
    return MagicMock(spec=RelatorioAcessos)


@pytest.fixture
def relatorio_controller(relatorio, controle_acesso):
    return RelatorioController(relatorio, controle_acesso)


def test_gestor_deve_gerar_o_relatorio(relatorio_controller, relatorio,
                                       tmp_path):
    relatorio.gerar.return_value = tmp_path / "relatorio.pdf"

    caminho = relatorio_controller.gerar_relatorio_acessos(
        usuario_com(Perfil.GESTOR))

    assert caminho == tmp_path / "relatorio.pdf"
    relatorio.gerar.assert_called_once_with()


@pytest.mark.parametrize("perfil", [Perfil.FISCAL, Perfil.FUNCIONARIO])
def test_c3_outros_perfis_devem_receber_acesso_negado(
        relatorio_controller, relatorio, perfil):
    with pytest.raises(AcessoNegadoError, match="Acesso negado"):
        relatorio_controller.gerar_relatorio_acessos(usuario_com(perfil))

    relatorio.gerar.assert_not_called()


def test_sem_usuario_autenticado_deve_negar(relatorio_controller, relatorio):
    with pytest.raises(AcessoNegadoError):
        relatorio_controller.gerar_relatorio_acessos(None)

    relatorio.gerar.assert_not_called()


def test_c3_perfil_negado_nao_deve_criar_arquivo(
        acessos, controle_acesso, tmp_path):
    controller = RelatorioController(
        RelatorioAcessosPdf(acessos, pasta_destino=tmp_path / "relatorios"),
        controle_acesso)

    with pytest.raises(AcessoNegadoError):
        controller.gerar_relatorio_acessos(usuario_com(Perfil.FUNCIONARIO))

    assert not (tmp_path / "relatorios").exists()
