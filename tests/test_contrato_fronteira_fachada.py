"""A fronteira de contrato ligada à fachada real, com os controllers e os
repositórios reais (e não mocks): o caminho que o main.py monta.

Cada nome da fachada que a fronteira chama precisa existir e ter a assinatura
certa; um nome repetido entre usuário e contrato (como `adicionar`) só aparece
aqui."""
from datetime import datetime

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController
from controle.facade_singleton_controller import FacadeSingletonController
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from fronteira.contrato_fronteira import ContratoFronteira
from persistencia.acesso_repositorio_memoria import AcessoRepositorioMemoria
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria


@pytest.fixture(autouse=True)
def limpar_singleton():
    FacadeSingletonController.resetar_instancia()
    yield
    FacadeSingletonController.resetar_instancia()


@pytest.fixture
def usuarios():
    return UsuarioRepositorioMemoria()


@pytest.fixture
def fachada(usuarios, hash_senha, controle_acesso):
    contratos = ContratoRepositorioMemoria()
    return FacadeSingletonController(
        usuario_controller=UsuarioController(
            usuarios, ValidadorCadastroUsuario(usuarios), hash_senha,
            controle_acesso),
        autenticacao_controller=AutenticacaoController(
            usuarios, AcessoRepositorioMemoria(), hash_senha),
        contrato_controller=ContratoController(
            repositorio=contratos,
            controle_acesso=controle_acesso,
            evidencia_repositorio=EvidenciaRepositorioMemoria(),
            usuario_repositorio=usuarios,
            relogio=lambda: datetime(2026, 10, 30, 9, 0, 0),
        ),
    )


@pytest.fixture
def fronteira(fachada, sessao, gestor):
    sessao.iniciar(gestor)
    return ContratoFronteira(fachada, sessao)


@pytest.fixture
def fiscal(usuarios):
    return usuarios.salvar(Usuario(
        0, "Carlos", "11144477735", "carlos@email.com", "carlos", "hash",
        Perfil.FISCAL))


def entradas(monkeypatch, *respostas):
    fila = iter(respostas)
    monkeypatch.setattr("builtins.input", lambda _: next(fila))


def cadastrar(fronteira, monkeypatch, numero="CT-1"):
    entradas(monkeypatch, numero, "Limpeza Brasil Ltda", "01/01/2026",
             "31/12/2026", "")
    fronteira.cadastrar_contrato()


def test_cadastrar_contrato_pela_fronteira_deve_gravar_e_confirmar(
        fronteira, fachada, gestor, monkeypatch, capsys):
    cadastrar(fronteira, monkeypatch)

    assert "Contrato cadastrado com sucesso!" in capsys.readouterr().out
    assert fachada.buscar_contrato_por_numero(gestor, "CT-1") is not None


def test_listar_contratos_pela_fronteira_deve_mostrar_o_cadastrado(
        fronteira, monkeypatch, capsys):
    cadastrar(fronteira, monkeypatch)
    capsys.readouterr()

    entradas(monkeypatch, "", "")
    fronteira.listar_contratos()

    saida = capsys.readouterr().out
    assert "CT-1" in saida and "Total: 1 contrato(s)" in saida


def test_editar_contrato_pela_fronteira_deve_alterar_a_empresa(
        fronteira, fachada, gestor, monkeypatch, capsys):
    cadastrar(fronteira, monkeypatch)
    capsys.readouterr()

    entradas(monkeypatch, "CT-1", "", "Nova Empresa", "", "", "")
    fronteira.editar_contrato()

    assert "Contrato atualizado com sucesso!" in capsys.readouterr().out
    assert fachada.buscar_contrato_por_numero(
        gestor, "CT-1").empresa_contratada == "Nova Empresa"


def test_vincular_e_desvincular_pela_fronteira(
        fronteira, fachada, gestor, fiscal, monkeypatch, capsys):
    cadastrar(fronteira, monkeypatch)

    entradas(monkeypatch, "CT-1", str(fiscal.id))
    fronteira.vincular_usuario()
    assert fiscal.id in fachada.buscar_contrato_por_numero(
        gestor, "CT-1").usuarios_vinculados
    assert "vinculado ao contrato CT-1 com sucesso!" in capsys.readouterr().out


def test_encerrar_contrato_pela_fronteira(
        fronteira, fachada, gestor, monkeypatch, capsys):
    cadastrar(fronteira, monkeypatch)

    entradas(monkeypatch, "CT-1", "s")
    fronteira.encerrar_contrato()

    assert fachada.buscar_contrato_por_numero(
        gestor, "CT-1").situacao.name == "ENCERRADO"


def test_remover_contrato_pela_fronteira(
        fronteira, fachada, gestor, monkeypatch, capsys):
    cadastrar(fronteira, monkeypatch)

    entradas(monkeypatch, "CT-1", "s")
    fronteira.remover_contrato()

    assert fachada.buscar_contrato_por_numero(gestor, "CT-1") is None


def test_funcionario_na_fronteira_deve_receber_acesso_negado(
        fachada, sessao, monkeypatch, capsys):
    sessao.iniciar(Usuario(
        7, "Ana", "52998224725", "ana@email.com", "ana", "hash",
        Perfil.FUNCIONARIO))
    entradas(monkeypatch, "CT-1", "Empresa", "01/01/2026", "31/12/2026", "")

    ContratoFronteira(fachada, sessao).cadastrar_contrato()

    assert "Acesso negado" in capsys.readouterr().out


def test_listar_com_situacao_invalida_nao_deve_derrubar_o_programa(
        fronteira, monkeypatch, capsys):
    cadastrar(fronteira, monkeypatch)
    capsys.readouterr()

    entradas(monkeypatch, "", "XYZ")
    fronteira.listar_contratos()

    saida = capsys.readouterr().out
    assert "Situação: use um destes valores: ATIVO, ENCERRADO" in saida
    assert "CT-1" not in saida


@pytest.mark.parametrize("situacao", ["ativo", "Encerrado", "TODOS", "todos"])
def test_listar_com_situacao_valida_nao_deve_dar_erro(
        fronteira, monkeypatch, capsys, situacao):
    cadastrar(fronteira, monkeypatch)
    capsys.readouterr()

    entradas(monkeypatch, "", situacao)
    fronteira.listar_contratos()

    assert "Erro" not in capsys.readouterr().out
