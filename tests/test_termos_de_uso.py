"""NF003 de Adequação a padrões (LGPD, art. 9º): o titular encontra, no
cadastro e no menu, a informação clara sobre o tratamento dos seus dados."""
import pytest

from fronteira.textos_legais import (
    POLITICA_DE_PRIVACIDADE,
    RESUMO_ANTES_DO_ACEITE,
    TERMOS_DE_USO,
)
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.usuario_fronteira import UsuarioFronteira

RESPOSTAS_DO_CADASTRO = [
    "Maria", "52998224725", "maria@email.com", "maria", "Senha@123",
    "Senha@123", "GESTOR",
]


@pytest.fixture
def fronteira(controller, autenticacao, painel, sessao):
    return UsuarioFronteira(
        controller, AutenticacaoFronteira(autenticacao, painel), sessao)


def simular_entradas(monkeypatch, *entradas):
    fila = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _: next(fila))


@pytest.mark.parametrize("trecho", [
    "Finalidade",
    "Dados coletados",
    "nome, CPF, e-mail, login e senha",
    "Conservação",
    "Seus direitos",
    "15 dias",
])
def test_politica_de_privacidade_deve_informar(trecho):
    assert trecho in POLITICA_DE_PRIVACIDADE


def test_termos_de_uso_devem_ter_texto():
    assert TERMOS_DE_USO.startswith("TERMOS DE USO")


def test_politica_nao_deve_prometer_cpf_completo():
    assert "mascarad" in POLITICA_DE_PRIVACIDADE


def test_menu_deve_oferecer_a_opcao_de_ver_os_termos(
        fronteira, monkeypatch, capsys):
    simular_entradas(monkeypatch, "0")
    fronteira.menu()
    assert "2 - Ver Termos de Uso e Política de Privacidade" in \
        capsys.readouterr().out


def test_opcao_2_do_menu_deve_exibir_os_dois_textos(
        fronteira, monkeypatch, capsys):
    simular_entradas(monkeypatch, "2", "0")
    fronteira.menu()
    saida = capsys.readouterr().out
    assert TERMOS_DE_USO in saida
    assert POLITICA_DE_PRIVACIDADE in saida


def test_cadastro_deve_exibir_o_resumo_antes_de_perguntar_o_aceite(
        fronteira, monkeypatch, capsys):
    respostas = iter(RESPOSTAS_DO_CADASTRO)
    exibido_antes_do_aceite = {}

    def entrada(prompt):
        if "Termos de Uso" in prompt:
            exibido_antes_do_aceite["texto"] = capsys.readouterr().out
            return "s"
        return next(respostas)

    monkeypatch.setattr("builtins.input", entrada)
    fronteira.cadastrar_usuario()

    assert RESUMO_ANTES_DO_ACEITE in exibido_antes_do_aceite["texto"]
    assert "opção 2 do menu" in RESUMO_ANTES_DO_ACEITE
