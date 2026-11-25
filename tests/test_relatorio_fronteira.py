"""RF 15 pelo painel: o Gestor gera o relatório de acessos e vê onde o
arquivo foi salvo (RN15.6); os outros perfis não veem a opção (C3)."""
from dataclasses import replace
from unittest.mock import MagicMock

import pytest
from pypdf import PdfReader

from controle.acesso.operacao import Operacao
from controle.facade_singleton_controller import FacadeSingletonController
from controle.relatorio.relatorio_acessos_pdf import RelatorioAcessosPdf
from controle.relatorio_controller import RelatorioController
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.persistencia_error import EscritaPersistenciaError
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.painel_fronteira import AcaoDoPainel
from fronteira.relatorio_fronteira import RelatorioFronteira
from fronteira.usuario_fronteira import UsuarioFronteira

ROTULO = "Gerar relatório de acessos"


@pytest.fixture
def pasta(tmp_path):
    return tmp_path / "relatorios"


@pytest.fixture
def fachada(controller, autenticacao, acessos, controle_acesso, pasta):
    relatorio = RelatorioAcessosPdf(acessos, pasta_destino=pasta)
    return FacadeSingletonController(
        usuario_controller=controller,
        autenticacao_controller=autenticacao,
        relatorio_controller=RelatorioController(relatorio, controle_acesso),
    )


@pytest.fixture
def fronteira(fachada, painel, sessao):
    relatorio_fronteira = RelatorioFronteira(fachada, sessao)
    painel.registrar(AcaoDoPainel(
        Operacao.GERAR_RELATORIO_ACESSOS, ROTULO,
        relatorio_fronteira.gerar_relatorio_acessos))
    return UsuarioFronteira(
        fachada, AutenticacaoFronteira(
            fachada, painel, ler_senha=lambda _: "Senha@123"), sessao)


def usar_o_menu(fronteira, monkeypatch, *entradas):
    fila = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _: next(fila))
    fronteira.menu()


def texto_do_pdf(pasta) -> str:
    (arquivo,) = pasta.iterdir()
    return "\n".join(p.extract_text() for p in PdfReader(arquivo).pages)


def test_c1_gestor_deve_gerar_o_pdf_com_os_acessos_do_login(
        fronteira, controller, dados_validos, pasta, monkeypatch, capsys):
    controller.adicionar(dados_validos)  # maria é GESTOR
    usar_o_menu(
        fronteira, monkeypatch,
        "3", "maria", "FISCAL",           # falha: perfil errado
        "3", "maria", "GESTOR", "0",      # sucesso; sai do painel
        "3", "maria", "GESTOR", "1", "0",  # sucesso; gera o relatório
        "0")

    saida = capsys.readouterr().out
    texto = texto_do_pdf(pasta)
    assert f"1 - {ROTULO}" in saida
    assert "Relatório gerado com sucesso!" in saida
    assert "Total de tentativas: 3" in texto
    assert "Sucessos: 2" in texto
    assert "Falhas: 1" in texto


def test_deve_informar_onde_o_arquivo_foi_salvo(
        fronteira, controller, dados_validos, pasta, monkeypatch, capsys):
    controller.adicionar(dados_validos)
    usar_o_menu(fronteira, monkeypatch,
                "3", "maria", "GESTOR", "1", "0", "0")

    (arquivo,) = pasta.iterdir()
    assert f"Arquivo salvo em: {arquivo.resolve()}" in capsys.readouterr().out


@pytest.mark.parametrize("perfil", ["FISCAL", "FUNCIONARIO"])
def test_c3_outros_perfis_nao_devem_ver_a_opcao(
        fronteira, controller, dados_validos, pasta, monkeypatch, capsys,
        perfil):
    controller.adicionar(replace(dados_validos, perfil=perfil))
    usar_o_menu(fronteira, monkeypatch,
                "3", "maria", perfil, "1", "0", "0")

    saida = capsys.readouterr().out
    assert ROTULO not in saida
    assert "Opção inválida" in saida
    assert not pasta.exists()


@pytest.mark.parametrize("perfil", [Perfil.FISCAL, Perfil.FUNCIONARIO, None])
def test_c3_acionada_por_fora_deve_responder_acesso_negado(
        fachada, sessao, pasta, capsys, perfil):
    if perfil is not None:
        sessao.iniciar(Usuario(1, "Ana", "52998224725", "ana@email.com",
                               "ana", "hash", perfil))

    RelatorioFronteira(fachada, sessao).gerar_relatorio_acessos()

    assert "Acesso negado" in capsys.readouterr().out
    assert not pasta.exists()


def test_erro_ao_gravar_deve_ser_exibido_sem_encerrar(sessao, gestor, capsys):
    fachada = MagicMock(spec=FacadeSingletonController)
    fachada.gerar_relatorio_acessos.side_effect = EscritaPersistenciaError(
        "disco cheio")
    sessao.iniciar(gestor)

    RelatorioFronteira(fachada, sessao).gerar_relatorio_acessos()

    assert "Erro de armazenamento: disco cheio" in capsys.readouterr().out
