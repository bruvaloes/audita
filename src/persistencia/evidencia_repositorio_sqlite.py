import sqlite3
from contextlib import contextmanager
from datetime import datetime

from entidade.evidencia import Evidencia
from entidade.origem_evidencia import OrigemEvidencia
from entidade.situacao_validacao import SituacaoValidacao
from persistencia.evidencia_repositorio import EvidenciaRepositorio
from excecao.persistencia_error import (
    ConexaoPersistenciaError,
    EscritaPersistenciaError,
    LeituraPersistenciaError,
)

COLUNAS_EVIDENCIA = (
    "id, caminho_imagem, enviada_em, geolocalizacao, origem, "
    "situacao, id_funcionario, numero_contrato, nome_tarefa"
)


class EvidenciaRepositorioSQLite(EvidenciaRepositorio):
    """Implementação do repositório de evidências utilizando SQLite.

    A imagem é armazenada em arquivo no sistema de arquivos; o banco
    guarda apenas o caminho (string) para esse arquivo.
    """

    def __init__(self, db_name: str = "evidencias.db"):
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
        CREATE TABLE IF NOT EXISTS evidencias (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            caminho_imagem   TEXT NOT NULL,
            enviada_em       TEXT NOT NULL,
            geolocalizacao   TEXT,
            origem           TEXT NOT NULL,
            situacao         TEXT NOT NULL,
            id_funcionario   INTEGER NOT NULL,
            numero_contrato  TEXT NOT NULL,
            nome_tarefa      TEXT NOT NULL
        )
        """
        try:
            with self._conectar() as conn:
                conn.execute(query)
        except sqlite3.Error as e:
            raise ConexaoPersistenciaError(
                f"Erro ao criar tabela no banco: {e}"
            ) from e

    def salvar(self, evidencia: Evidencia) -> Evidencia:
        query = """
        INSERT INTO evidencias
            (caminho_imagem, enviada_em, geolocalizacao, origem,
             situacao, id_funcionario, numero_contrato, nome_tarefa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._conectar() as conn:
                cursor = conn.execute(query, (
                    evidencia.caminho_imagem,
                    evidencia.enviada_em.isoformat(),
                    evidencia.geolocalizacao,
                    evidencia.origem.value,
                    evidencia.situacao.value,
                    evidencia.id_funcionario,
                    evidencia.numero_contrato,
                    evidencia.nome_tarefa,
                ))
                evidencia.id = cursor.lastrowid
                return evidencia
        except sqlite3.Error as e:
            raise EscritaPersistenciaError(
                f"Erro ao salvar evidência no banco: {e}"
            ) from e

    def buscar_por_id(self, id_evidencia: int) -> Evidencia | None:
        query = f"SELECT {COLUNAS_EVIDENCIA} FROM evidencias WHERE id = ?"
        try:
            with self._conectar() as conn:
                row = conn.execute(query, (id_evidencia,)).fetchone()
        except sqlite3.Error as e:
            raise LeituraPersistenciaError(
                f"Erro ao buscar evidência por id: {e}"
            ) from e
        return self._montar_evidencia(row) if row else None

    def listar(
        self,
        numero_contrato: str | None = None,
        id_funcionario: int | None = None,
    ) -> list[Evidencia]:
        condicoes: list[str] = []
        parametros: list = []

        if numero_contrato is not None:
            condicoes.append("numero_contrato = ?")
            parametros.append(numero_contrato)
        if id_funcionario is not None:
            condicoes.append("id_funcionario = ?")
            parametros.append(id_funcionario)

        where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
        query = f"SELECT {COLUNAS_EVIDENCIA} FROM evidencias {where} ORDER BY id"

        try:
            with self._conectar() as conn:
                rows = conn.execute(query, parametros).fetchall()
            return [self._montar_evidencia(row) for row in rows]
        except sqlite3.Error as e:
            raise LeituraPersistenciaError(
                f"Erro ao listar evidências: {e}"
            ) from e

    def atualizar_situacao(
        self, id_evidencia: int, situacao: SituacaoValidacao
    ) -> None:
        query = "UPDATE evidencias SET situacao = ? WHERE id = ?"
        try:
            with self._conectar() as conn:
                conn.execute(query, (situacao.value, id_evidencia))
        except sqlite3.Error as e:
            raise EscritaPersistenciaError(
                f"Erro ao atualizar situação da evidência no banco: {e}"
            ) from e

    def _montar_evidencia(self, row: tuple) -> Evidencia:
        return Evidencia(
            id=row[0],
            caminho_imagem=row[1],
            enviada_em=datetime.fromisoformat(row[2]),
            geolocalizacao=row[3],
            origem=OrigemEvidencia(row[4]),
            situacao=SituacaoValidacao(row[5]),
            id_funcionario=row[6],
            numero_contrato=row[7],
            nome_tarefa=row[8],
        )
