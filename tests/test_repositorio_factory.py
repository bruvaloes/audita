"""Testes da RepositorioFactory e da função escolher_repositorio."""
import pytest

from excecao.persistencia_error import ConexaoPersistenciaError, PersistenciaError
from infraestrutura.acesso_repositorio_memoria import AcessoRepositorioMemoria
from infraestrutura.acesso_repositorio_sqlite import AcessoRepositorioSQLite
from infraestrutura.contrato_repositorio_memoria import ContratoRepositorioMemoria
from infraestrutura.contrato_repositorio_sqlite import ContratoRepositorioSQLite
from infraestrutura.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from infraestrutura.evidencia_repositorio_sqlite import EvidenciaRepositorioSQLite
from infraestrutura.repositorio_factory import (
    RepositorioFactory,
    RepositorioFactoryMemoria,
    RepositorioFactorySQLite,
)
from infraestrutura.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from infraestrutura.usuario_repositorio_sqlite import UsuarioRepositorioSQLite
from log.log_auditoria import LogAuditoria
from log.log_auditoria_adapter import LogAuditoriaAdapter
from log.log_auditoria_memoria import LogAuditoriaMemoria
from main import escolher_repositorio, escolher_repositorios
from negocio.acesso_repositorio import AcessoRepositorio
from negocio.contrato_repositorio import ContratoRepositorio
from negocio.evidencia_repositorio import EvidenciaRepositorio
from negocio.usuario_repositorio import UsuarioRepositorio


def test_factory_cria_repositorios_em_memoria():
    factory = RepositorioFactoryMemoria()

    assert isinstance(factory, RepositorioFactory)
    usuario_repo = factory.criar_usuario_repositorio()
    acesso_repo = factory.criar_acesso_repositorio()
    contrato_repo = factory.criar_contrato_repositorio()
    evidencia_repo = factory.criar_evidencia_repositorio()
    log_auditoria = factory.criar_log_auditoria()

    assert isinstance(usuario_repo, UsuarioRepositorioMemoria)
    assert isinstance(usuario_repo, UsuarioRepositorio)
    assert isinstance(acesso_repo, AcessoRepositorioMemoria)
    assert isinstance(acesso_repo, AcessoRepositorio)
    assert isinstance(contrato_repo, ContratoRepositorioMemoria)
    assert isinstance(contrato_repo, ContratoRepositorio)
    assert isinstance(evidencia_repo, EvidenciaRepositorioMemoria)
    assert isinstance(evidencia_repo, EvidenciaRepositorio)
    assert isinstance(log_auditoria, LogAuditoriaMemoria)
    assert isinstance(log_auditoria, LogAuditoria)

    # Verifica também a criação agregada (criar_todos)
    repos = factory.criar_todos()
    assert len(repos) == 5
    assert isinstance(repos[0], UsuarioRepositorioMemoria)
    assert isinstance(repos[1], AcessoRepositorioMemoria)
    assert isinstance(repos[2], ContratoRepositorioMemoria)
    assert isinstance(repos[3], EvidenciaRepositorioMemoria)
    assert isinstance(repos[4], LogAuditoriaMemoria)


def test_factory_cria_repositorios_sqlite(tmp_path):
    db_u = str(tmp_path / "usuarios.db")
    db_c = str(tmp_path / "contratos.db")
    db_e = str(tmp_path / "evidencias.db")
    log_p = str(tmp_path / "auditoria.log")

    factory = RepositorioFactorySQLite(
        db_usuarios=db_u,
        db_contratos=db_c,
        db_evidencias=db_e,
        caminho_log=log_p,
    )

    assert isinstance(factory, RepositorioFactory)
    usuario_repo = factory.criar_usuario_repositorio()
    acesso_repo = factory.criar_acesso_repositorio()
    contrato_repo = factory.criar_contrato_repositorio()
    evidencia_repo = factory.criar_evidencia_repositorio()
    log_auditoria = factory.criar_log_auditoria()

    assert isinstance(usuario_repo, UsuarioRepositorioSQLite)
    assert isinstance(usuario_repo, UsuarioRepositorio)
    assert isinstance(acesso_repo, AcessoRepositorioSQLite)
    assert isinstance(acesso_repo, AcessoRepositorio)
    assert isinstance(contrato_repo, ContratoRepositorioSQLite)
    assert isinstance(contrato_repo, ContratoRepositorio)
    assert isinstance(evidencia_repo, EvidenciaRepositorioSQLite)
    assert isinstance(evidencia_repo, EvidenciaRepositorio)
    assert isinstance(log_auditoria, LogAuditoriaAdapter)
    assert isinstance(log_auditoria, LogAuditoria)

    # Verifica também a criação agregada (criar_todos)
    repos = factory.criar_todos()
    assert len(repos) == 5
    assert isinstance(repos[0], UsuarioRepositorioSQLite)
    assert isinstance(repos[1], AcessoRepositorioSQLite)
    assert isinstance(repos[2], ContratoRepositorioSQLite)
    assert isinstance(repos[3], EvidenciaRepositorioSQLite)
    assert isinstance(repos[4], LogAuditoriaAdapter)


def test_escolher_repositorio_opcao_invalida(monkeypatch, capsys):
    entradas = iter(["invalido", "99", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    repositorios = escolher_repositorio()

    saida = capsys.readouterr().out
    assert "Opção inválida" in saida
    assert "Usando: Em memória" in saida
    assert len(repositorios) == 5
    assert isinstance(repositorios[0], UsuarioRepositorioMemoria)


def test_escolher_repositorio_falha_de_conexao(monkeypatch, capsys):
    entradas = iter(["1", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    def falhar_sqlite(*args, **kwargs):
        raise ConexaoPersistenciaError("Falha de conexão com SQLite")

    monkeypatch.setattr(
        "infraestrutura.repositorio_factory.RepositorioFactorySQLite.criar_todos",
        falhar_sqlite,
    )

    repositorios = escolher_repositorio()

    saida = capsys.readouterr().out
    assert "Falha de conexão com SQLite" in saida
    assert "Escolha outro mecanismo de armazenamento." in saida
    assert "Usando: Em memória" in saida
    assert len(repositorios) == 5
    assert isinstance(repositorios[0], UsuarioRepositorioMemoria)


def test_escolher_repositorios_opcao_invalida(monkeypatch, capsys):
    """Garante compatibilidade para o nome no plural."""
    entradas = iter(["invalido", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    repositorios = escolher_repositorios()
    saida = capsys.readouterr().out
    assert "Opção inválida" in saida
    assert "Usando: Em memória" in saida
    assert len(repositorios) == 5


def test_escolher_repositorios_falha_de_conexao(monkeypatch, capsys):
    """Garante compatibilidade para o nome no plural."""
    entradas = iter(["1", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    def falhar_sqlite(*args, **kwargs):
        raise ConexaoPersistenciaError("Falha de conexão com SQLite")

    monkeypatch.setattr(
        "infraestrutura.repositorio_factory.RepositorioFactorySQLite.criar_todos",
        falhar_sqlite,
    )

    repositorios = escolher_repositorios()
    saida = capsys.readouterr().out
    assert "Falha de conexão com SQLite" in saida
    assert len(repositorios) == 5

