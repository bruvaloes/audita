"""Contrato de AcessoRepositorio.

Toda implementação deve passar nestes testes (Liskov): para cobrir uma nova,
basta incluí-la na fixture `repositorio_implementacao`.
"""
from datetime import datetime

import pytest

from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from persistencia.acesso_repositorio import AcessoRepositorio
from persistencia.acesso_repositorio_memoria import AcessoRepositorioMemoria
from persistencia.acesso_repositorio_sqlite import AcessoRepositorioSQLite

MOMENTO = datetime(2026, 10, 28, 14, 30, 5)


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio_implementacao(request, tmp_path) -> AcessoRepositorio:
    if request.param == "memoria":
        return AcessoRepositorioMemoria()
    return AcessoRepositorioSQLite(str(tmp_path / "contrato.db"))


def novo_acesso(usuario_id=1, perfil=Perfil.GESTOR,
                resultado=ResultadoAcesso.SUCESSO) -> Acesso:
    return Acesso(0, usuario_id, perfil, MOMENTO, resultado)


def test_deve_comecar_sem_acessos(repositorio_implementacao):
    assert repositorio_implementacao.listar_todos() == []


def test_deve_atribuir_ids_sequenciais_ao_salvar(repositorio_implementacao):
    primeiro = repositorio_implementacao.salvar(novo_acesso())
    segundo = repositorio_implementacao.salvar(novo_acesso())

    assert (primeiro.id, segundo.id) == (1, 2)


def test_deve_listar_na_ordem_em_que_foram_salvos(repositorio_implementacao):
    primeiro = repositorio_implementacao.salvar(novo_acesso())
    segundo = repositorio_implementacao.salvar(
        novo_acesso(2, Perfil.FISCAL, ResultadoAcesso.CREDENCIAIS_INVALIDAS))

    assert repositorio_implementacao.listar_todos() == [primeiro, segundo]


def test_deve_preservar_todos_os_campos(repositorio_implementacao):
    repositorio_implementacao.salvar(
        novo_acesso(7, Perfil.FUNCIONARIO, ResultadoAcesso.BLOQUEADO))

    acesso = repositorio_implementacao.listar_todos()[0]

    assert (acesso.usuario_id, acesso.perfil, acesso.data_hora,
            acesso.resultado) == (7, Perfil.FUNCIONARIO, MOMENTO,
                                  ResultadoAcesso.BLOQUEADO)


def test_deve_aceitar_acesso_sem_usuario_e_sem_perfil(
        repositorio_implementacao):
    repositorio_implementacao.salvar(
        novo_acesso(None, None, ResultadoAcesso.CREDENCIAIS_INVALIDAS))

    acesso = repositorio_implementacao.listar_todos()[0]

    assert (acesso.usuario_id, acesso.perfil) == (None, None)
