"""Contrato de EvidenciaRepositorio.

Toda implementação deve passar nestes testes (Liskov): para cobrir uma nova,
basta incluí-la na fixture `repositorio_implementacao`.
"""
from datetime import datetime
import sqlite3

import pytest

from entidade.evidencia import Evidencia
from entidade.origem_evidencia import OrigemEvidencia
from entidade.situacao_validacao import SituacaoValidacao
from excecao.persistencia_error import (
    ConexaoPersistenciaError,
    EscritaPersistenciaError,
    LeituraPersistenciaError,
)
from persistencia.evidencia_repositorio import EvidenciaRepositorio
from persistencia.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from persistencia.evidencia_repositorio_sqlite import EvidenciaRepositorioSQLite


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio_implementacao(request, tmp_path) -> EvidenciaRepositorio:
    if request.param == "memoria":
        return EvidenciaRepositorioMemoria()
    return EvidenciaRepositorioSQLite(str(tmp_path / "evidencias.db"))


def nova_evidencia(
    caminho_imagem: str = "storage/evidencias/foto_001.jpg",
    enviada_em: datetime | None = None,
    geolocalizacao: str | None = "-23.550520,-46.633308",
    origem: OrigemEvidencia = OrigemEvidencia.CAMERA,
    situacao: SituacaoValidacao = SituacaoValidacao.PENDENTE,
    id_funcionario: int = 1,
    numero_contrato: str = "CT-2024-001",
    nome_tarefa: str = "Instalação de postes",
) -> Evidencia:
    return Evidencia(
        id=0,
        caminho_imagem=caminho_imagem,
        enviada_em=enviada_em or datetime(2026, 10, 28, 10, 30, 0),
        geolocalizacao=geolocalizacao,
        origem=origem,
        situacao=situacao,
        id_funcionario=id_funcionario,
        numero_contrato=numero_contrato,
        nome_tarefa=nome_tarefa,
    )


def test_deve_atribuir_ids_sequenciais_ao_salvar(repositorio_implementacao):
    primeira = repositorio_implementacao.salvar(nova_evidencia())
    segunda = repositorio_implementacao.salvar(
        nova_evidencia(caminho_imagem="storage/evidencias/foto_002.jpg")
    )

    assert (primeira.id, segunda.id) == (1, 2)


def test_deve_listar_na_ordem_em_que_foram_salvas(repositorio_implementacao):
    primeira = repositorio_implementacao.salvar(nova_evidencia())
    segunda = repositorio_implementacao.salvar(
        nova_evidencia(caminho_imagem="storage/evidencias/foto_002.jpg")
    )

    assert repositorio_implementacao.listar() == [primeira, segunda]


def test_deve_buscar_por_id(repositorio_implementacao):
    evidencia = repositorio_implementacao.salvar(nova_evidencia())

    assert repositorio_implementacao.buscar_por_id(evidencia.id) == evidencia


def test_deve_retornar_none_quando_nao_encontrar_id(repositorio_implementacao):
    assert repositorio_implementacao.buscar_por_id(999) is None


def test_deve_listar_filtrando_por_contrato(repositorio_implementacao):
    ev1 = repositorio_implementacao.salvar(nova_evidencia(numero_contrato="CT-001"))
    ev2 = repositorio_implementacao.salvar(nova_evidencia(numero_contrato="CT-002"))
    ev3 = repositorio_implementacao.salvar(nova_evidencia(numero_contrato="CT-001"))

    resultado_ct001 = repositorio_implementacao.listar(numero_contrato="CT-001")
    resultado_ct002 = repositorio_implementacao.listar(numero_contrato="CT-002")

    assert resultado_ct001 == [ev1, ev3]
    assert resultado_ct002 == [ev2]


def test_deve_listar_filtrando_por_funcionario(repositorio_implementacao):
    ev1 = repositorio_implementacao.salvar(nova_evidencia(id_funcionario=10))
    ev2 = repositorio_implementacao.salvar(nova_evidencia(id_funcionario=20))

    resultado_f10 = repositorio_implementacao.listar(id_funcionario=10)
    resultado_f20 = repositorio_implementacao.listar(id_funcionario=20)

    assert resultado_f10 == [ev1]
    assert resultado_f20 == [ev2]


def test_deve_listar_combinando_filtros_de_contrato_e_funcionario(
    repositorio_implementacao,
):
    ev1 = repositorio_implementacao.salvar(
        nova_evidencia(numero_contrato="CT-001", id_funcionario=10)
    )
    repositorio_implementacao.salvar(
        nova_evidencia(numero_contrato="CT-001", id_funcionario=20)
    )
    repositorio_implementacao.salvar(
        nova_evidencia(numero_contrato="CT-002", id_funcionario=10)
    )

    resultado = repositorio_implementacao.listar(
        numero_contrato="CT-001", id_funcionario=10
    )
    assert resultado == [ev1]


def test_deve_atualizar_situacao_da_evidencia(repositorio_implementacao):
    evidencia = repositorio_implementacao.salvar(
        nova_evidencia(situacao=SituacaoValidacao.PENDENTE)
    )

    repositorio_implementacao.atualizar_situacao(
        evidencia.id, SituacaoValidacao.APROVADA
    )

    atualizada = repositorio_implementacao.buscar_por_id(evidencia.id)
    assert atualizada is not None
    assert atualizada.situacao == SituacaoValidacao.APROVADA
    assert atualizada.nome_tarefa == evidencia.nome_tarefa
    assert atualizada.caminho_imagem == evidencia.caminho_imagem


def test_atualizar_situacao_evidencia_inexistente_nao_lanca_erro(
    repositorio_implementacao,
):
    repositorio_implementacao.atualizar_situacao(999, SituacaoValidacao.RECUSADA)


# Testes específicos de persistência e exceções para SQLite
def test_banco_inacessivel_lanca_conexao_persistencia_error(tmp_path):
    with pytest.raises(ConexaoPersistenciaError):
        EvidenciaRepositorioSQLite(str(tmp_path / "inexistente" / "teste.db"))


def test_tabela_inexistente_lanca_leitura_persistencia_error(tmp_path):
    caminho = str(tmp_path / "teste.db")
    repo = EvidenciaRepositorioSQLite(caminho)
    with sqlite3.connect(caminho) as conn:
        conn.execute("DROP TABLE evidencias")
    with pytest.raises(LeituraPersistenciaError):
        repo.listar()


def test_tabela_inexistente_lanca_escrita_persistencia_error_ao_salvar(tmp_path):
    caminho = str(tmp_path / "teste.db")
    repo = EvidenciaRepositorioSQLite(caminho)
    with sqlite3.connect(caminho) as conn:
        conn.execute("DROP TABLE evidencias")
    with pytest.raises(EscritaPersistenciaError):
        repo.salvar(nova_evidencia())


def test_tabela_inexistente_lanca_escrita_persistencia_error_ao_atualizar(tmp_path):
    caminho = str(tmp_path / "teste.db")
    repo = EvidenciaRepositorioSQLite(caminho)
    with sqlite3.connect(caminho) as conn:
        conn.execute("DROP TABLE evidencias")
    with pytest.raises(EscritaPersistenciaError):
        repo.atualizar_situacao(1, SituacaoValidacao.APROVADA)
