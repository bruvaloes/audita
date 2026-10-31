import json
import sqlite3
from contextlib import contextmanager
from datetime import date

from entidade.contrato import Contrato
from entidade.situacao_contrato import SituacaoContrato
from persistencia.contrato_repositorio import ContratoRepositorio
from excecao.persistencia_error import (
    ConexaoPersistenciaError,
    EscritaPersistenciaError,
    LeituraPersistenciaError,
)

COLUNAS_CONTRATO = (
    "id, numero, empresa_contratada, vigencia_inicio, vigencia_fim, "
    "arquivo, situacao, usuarios_vinculados"
)


class ContratoRepositorioSQLite(ContratoRepositorio):
    """Implementação do repositório de contratos utilizando SQLite."""

    def __init__(self, db_name: str = "contratos.db"):
        self.db_name = db_name
        self._criar_tabela()

    @contextmanager
    def _conectar(self):
        try:
            conn = sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            raise ConexaoPersistenciaError(
                f"Erro ao conectar ao banco de dados: {e}"
            ) from e
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _criar_tabela(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS contratos (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            numero             TEXT UNIQUE NOT NULL,
            empresa_contratada TEXT NOT NULL,
            vigencia_inicio    TEXT NOT NULL,
            vigencia_fim       TEXT NOT NULL,
            arquivo            TEXT,
            situacao           TEXT NOT NULL,
            usuarios_vinculados TEXT NOT NULL DEFAULT '[]'
        )
        """
        try:
            with self._conectar() as conn:
                conn.execute(query)
        except sqlite3.Error as e:
            raise ConexaoPersistenciaError(
                f"Erro ao criar tabela no banco: {e}"
            ) from e

    def salvar(self, contrato: Contrato) -> Contrato:
        query = """
        INSERT INTO contratos
            (numero, empresa_contratada, vigencia_inicio, vigencia_fim,
             arquivo, situacao, usuarios_vinculados)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._conectar() as conn:
                cursor = conn.execute(query, (
                    contrato.numero,
                    contrato.empresa_contratada,
                    contrato.vigencia_inicio.isoformat(),
                    contrato.vigencia_fim.isoformat(),
                    contrato.arquivo,
                    contrato.situacao.value,
                    json.dumps(contrato.usuarios_vinculados),
                ))
                contrato.id = cursor.lastrowid
                return contrato
        except sqlite3.Error as e:
            raise EscritaPersistenciaError(
                f"Erro ao salvar contrato no banco: {e}"
            ) from e

    def listar(self) -> list[Contrato]:
        query = f"SELECT {COLUNAS_CONTRATO} FROM contratos ORDER BY id"
        try:
            with self._conectar() as conn:
                rows = conn.execute(query).fetchall()
            return [self._montar_contrato(row) for row in rows]
        except sqlite3.Error as e:
            raise LeituraPersistenciaError(
                f"Erro ao listar contratos: {e}"
            ) from e

    def buscar_por_numero(self, numero: str) -> Contrato | None:
        query = f"SELECT {COLUNAS_CONTRATO} FROM contratos WHERE numero = ?"
        try:
            with self._conectar() as conn:
                row = conn.execute(query, (numero,)).fetchone()
        except sqlite3.Error as e:
            raise LeituraPersistenciaError(
                f"Erro ao buscar contrato por numero: {e}"
            ) from e
        return self._montar_contrato(row) if row else None

    def atualizar(self, contrato: Contrato) -> None:
        query = """
        UPDATE contratos
        SET empresa_contratada  = ?,
            vigencia_inicio     = ?,
            vigencia_fim        = ?,
            arquivo             = ?,
            situacao            = ?,
            usuarios_vinculados = ?
        WHERE numero = ?
        """
        try:
            with self._conectar() as conn:
                conn.execute(query, (
                    contrato.empresa_contratada,
                    contrato.vigencia_inicio.isoformat(),
                    contrato.vigencia_fim.isoformat(),
                    contrato.arquivo,
                    contrato.situacao.value,
                    json.dumps(contrato.usuarios_vinculados),
                    contrato.numero,
                ))
        except sqlite3.Error as e:
            raise EscritaPersistenciaError(
                f"Erro ao atualizar contrato no banco: {e}"
            ) from e

    def remover(self, numero: str) -> None:
        query = "DELETE FROM contratos WHERE numero = ?"
        try:
            with self._conectar() as conn:
                conn.execute(query, (numero,))
        except sqlite3.Error as e:
            raise EscritaPersistenciaError(
                f"Erro ao remover contrato do banco: {e}"
            ) from e

    def _montar_contrato(self, row: tuple) -> Contrato:
        return Contrato(
            id=row[0],
            numero=row[1],
            empresa_contratada=row[2],
            vigencia_inicio=date.fromisoformat(row[3]),
            vigencia_fim=date.fromisoformat(row[4]),
            arquivo=row[5],
            situacao=SituacaoContrato(row[6]),
            usuarios_vinculados=json.loads(row[7]),
        )
