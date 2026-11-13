"""RF 16: a quantidade de entidades no menu principal, com a fachada real."""
from unittest.mock import MagicMock

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController
from controle.facade_singleton_controller import FacadeSingletonController
from controle.sessao import Sessao
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.persistencia_error import LeituraPersistenciaError
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.usuario_fronteira import UsuarioFronteira
from infraestrutura.acesso_repositorio_memoria import AcessoRepositorioMemoria
from infraestrutura.contrato_repositorio_memoria import ContratoRepositorioMemoria
from infraestrutura.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from infraestrutura.usuario_repositorio_memoria import UsuarioRepositorioMemoria


@pytest.fixture
def usuarios():
    return UsuarioRepositorioMemoria()


@pytest.fixture
def fachada(usuarios, hash_senha):
    controle_acesso = ControleAcesso()
    evidencias = EvidenciaRepositorioMemoria()
    return FacadeSingletonController(
        usuario_controller=UsuarioController(
            usuarios, ValidadorCadastroUsuario(usuarios), hash_senha,
            controle_acesso),
        autenticacao_controller=AutenticacaoController(
            usuarios, AcessoRepositorioMemoria(), hash_senha),
        contrato_controller=ContratoController(
            repositorio=ContratoRepositorioMemoria(),
            controle_acesso=controle_acesso,
            evidencia_repositorio=evidencias,
            usuario_repositorio=usuarios,
        ),
        evidencia_repositorio=evidencias,
    )


@pytest.fixture
def fronteira(fachada):
    return UsuarioFronteira(
        fachada, MagicMock(spec=AutenticacaoFronteira), Sessao())


def test_deve_exibir_zero_quando_nao_ha_entidades(fronteira, capsys):
    fronteira.exibir_quantidade_entidades()

    saida = capsys.readouterr().out
    assert "Usuários: 0" in saida
    assert "Contratos: 0" in saida
    assert "Evidências: 0" in saida
    assert "Total: 0" in saida


def test_deve_exibir_quantidade_de_cada_tipo_e_total(
        fronteira, usuarios, capsys):
    usuarios.salvar(Usuario(
        0, "Maria", "52998224725", "maria@email.com", "maria", "hash",
        Perfil.GESTOR))

    fronteira.exibir_quantidade_entidades()

    saida = capsys.readouterr().out
    assert "Usuários: 1" in saida
    assert "Total: 1" in saida


def test_opcao_do_menu_deve_funcionar_sem_login(
        fronteira, monkeypatch, capsys):
    respostas = iter(["4", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    fronteira.menu()

    assert "--- Entidades cadastradas ---" in capsys.readouterr().out


def test_deve_mostrar_erro_de_armazenamento_sem_encerrar(
        fachada, monkeypatch, capsys):
    fronteira = UsuarioFronteira(
        fachada, MagicMock(spec=AutenticacaoFronteira), Sessao())

    def falhar():
        raise LeituraPersistenciaError("banco indisponível")

    monkeypatch.setattr(fachada, "contar_entidades_detalhado", falhar)

    fronteira.exibir_quantidade_entidades()

    assert ("Erro de armazenamento: banco indisponível"
            in capsys.readouterr().out)

