"""Contrato de ContratoRepositorio.

Toda implementação deve passar nestes testes (Liskov): para cobrir uma nova,
basta incluí-la na fixture `repositorio_implementacao`.
"""
from datetime import date
import sqlite3

import pytest

from entidade.contrato import Contrato
from entidade.situacao_contrato import SituacaoContrato
from excecao.persistencia_error import (
    ConexaoPersistenciaError,
    EscritaPersistenciaError,
    LeituraPersistenciaError,
)
from persistencia.contrato_repositorio import ContratoRepositorio
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.contrato_repositorio_sqlite import ContratoRepositorioSQLite


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio_implementacao(request, tmp_path) -> ContratoRepositorio:
    if request.param == "memoria":
        return ContratoRepositorioMemoria()
    return ContratoRepositorioSQLite(str(tmp_path / "contrato.db"))


def novo_contrato(
    numero: str = "CT-2024-001",
    empresa: str = "Empresa Alpha Ltda",
    situacao: SituacaoContrato = SituacaoContrato.ATIVO,
    usuarios: list[int] | None = None,
) -> Contrato:
    return Contrato(
        id=0,
        numero=numero,
        empresa_contratada=empresa,
        vigencia_inicio=date(2024, 1, 1),
        vigencia_fim=date(2024, 12, 31),
        arquivo="contrato_alpha.pdf",
        situacao=situacao,
        usuarios_vinculados=usuarios if usuarios is not None else [1, 2],
    )


def test_deve_atribuir_ids_sequenciais_ao_salvar(repositorio_implementacao):
    primeiro = repositorio_implementacao.salvar(novo_contrato())
    segundo = repositorio_implementacao.salvar(
        novo_contrato(numero="CT-2024-002", empresa="Empresa Beta S/A")
    )

    assert (primeiro.id, segundo.id) == (1, 2)


def test_deve_listar_na_ordem_em_que_foram_salvos(repositorio_implementacao):
    primeiro = repositorio_implementacao.salvar(novo_contrato())
    segundo = repositorio_implementacao.salvar(
        novo_contrato(numero="CT-2024-002", empresa="Empresa Beta S/A")
    )

    assert repositorio_implementacao.listar() == [primeiro, segundo]


def test_deve_buscar_por_numero(repositorio_implementacao):
    contrato = repositorio_implementacao.salvar(novo_contrato())

    assert repositorio_implementacao.buscar_por_numero(contrato.numero) == contrato


def test_deve_retornar_none_quando_nao_encontrar(repositorio_implementacao):
    assert repositorio_implementacao.buscar_por_numero("CT-INEXISTENTE") is None


def test_deve_atualizar_contrato(repositorio_implementacao):
    contrato = repositorio_implementacao.salvar(novo_contrato())

    contrato.empresa_contratada = "Empresa Alpha Atualizada"
    contrato.situacao = SituacaoContrato.ENCERRADO
    contrato.usuarios_vinculados = [1, 2, 3]
    repositorio_implementacao.atualizar(contrato)

    atualizado = repositorio_implementacao.buscar_por_numero(contrato.numero)
    assert atualizado is not None
    assert atualizado.empresa_contratada == "Empresa Alpha Atualizada"
    assert atualizado.situacao == SituacaoContrato.ENCERRADO
    assert atualizado.usuarios_vinculados == [1, 2, 3]


def test_deve_remover_contrato(repositorio_implementacao):
    contrato = repositorio_implementacao.salvar(novo_contrato())

    repositorio_implementacao.remover(contrato.numero)

    assert repositorio_implementacao.buscar_por_numero(contrato.numero) is None
    assert repositorio_implementacao.listar() == []


def test_remover_inexistente_nao_lanca_erro(repositorio_implementacao):
    repositorio_implementacao.remover("CT-INEXISTENTE")


def test_numero_duplicado_deve_ser_recusado_e_manter_o_contrato_original(
        repositorio_implementacao):
    repositorio_implementacao.salvar(novo_contrato("CT-1", "Empresa Original"))

    with pytest.raises(EscritaPersistenciaError):
        repositorio_implementacao.salvar(novo_contrato("CT-1", "Outra Empresa"))

    contratos = repositorio_implementacao.listar()
    assert [c.empresa_contratada for c in contratos] == ["Empresa Original"]


# Testes específicos de persistência e exceções para SQLite
def test_salvar_numero_duplicado_lanca_escrita_persistencia_error(tmp_path):
    repo = ContratoRepositorioSQLite(str(tmp_path / "teste.db"))
    repo.salvar(novo_contrato(numero="CT-DUPLICADO"))

    with pytest.raises(EscritaPersistenciaError):
        repo.salvar(novo_contrato(numero="CT-DUPLICADO"))


def test_banco_inacessivel_lanca_conexao_persistencia_error(tmp_path):
    with pytest.raises(ConexaoPersistenciaError):
        ContratoRepositorioSQLite(str(tmp_path / "inexistente" / "teste.db"))


def test_tabela_inexistente_lanca_leitura_persistencia_error(tmp_path):
    caminho = str(tmp_path / "teste.db")
    repo = ContratoRepositorioSQLite(caminho)
    with sqlite3.connect(caminho) as conn:
        conn.execute("DROP TABLE contratos")
    with pytest.raises(LeituraPersistenciaError):
        repo.listar()
