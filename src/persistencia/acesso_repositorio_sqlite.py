import sqlite3
from datetime import datetime

from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from excecao.persistencia_error import (
    ConexaoPersistenciaError,
    EscritaPersistenciaError,
    LeituraPersistenciaError,
)
from persistencia.acesso_repositorio import AcessoRepositorio

COLUNAS_ACESSO = "id, usuario_id, perfil, data_hora, resultado"


class AcessoRepositorioSQLite(AcessoRepositorio):
    """Repositório de acessos em SQLite.

    Por padrão usa o mesmo arquivo dos usuários, para que um só banco guarde
    os dois. Não há chave estrangeira para `usuarios`: o registro de acesso
    deve valer por si, mesmo que o cadastro mude depois.
    """

    def __init__(self, db_name: str = "usuarios.db"):
        self.db_name = db_name
        self._criar_tabela()

    def _conectar(self) -> sqlite3.Connection:
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            raise ConexaoPersistenciaError(f"Erro ao conectar ao banco de dados: {e}") from e

    def _criar_tabela(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            perfil TEXT,
            data_hora TEXT NOT NULL,
            resultado TEXT NOT NULL
        )
        """
        try:
            with self._conectar() as conn:
                conn.execute(query)
        except sqlite3.Error as e:
            raise ConexaoPersistenciaError(f"Erro ao criar tabela no banco: {e}") from e

    def salvar(self, acesso: Acesso) -> Acesso:
        query = """
        INSERT INTO acessos (usuario_id, perfil, data_hora, resultado)
        VALUES (?, ?, ?, ?)
        """
        try:
            with self._conectar() as conn:
                cursor = conn.execute(query, (
                    acesso.usuario_id,
                    acesso.perfil.value if acesso.perfil else None,
                    acesso.data_hora.isoformat(),
                    acesso.resultado.value,
                ))
                acesso.id = cursor.lastrowid
                return acesso
        except sqlite3.Error as e:
            raise EscritaPersistenciaError(f"Erro ao salvar acesso no banco: {e}") from e

    def listar_todos(self) -> list[Acesso]:
        query = f"SELECT {COLUNAS_ACESSO} FROM acessos ORDER BY id"
        try:
            with self._conectar() as conn:
                linhas = conn.execute(query).fetchall()
        except sqlite3.Error as e:
            raise LeituraPersistenciaError(f"Erro ao listar acessos: {e}") from e
        return [self._montar_acesso(linha) for linha in linhas]

    @staticmethod
    def _montar_acesso(linha: tuple) -> Acesso:
        return Acesso(
            id=linha[0],
            usuario_id=linha[1],
            perfil=Perfil(linha[2]) if linha[2] else None,
            data_hora=datetime.fromisoformat(linha[3]),
            resultado=ResultadoAcesso(linha[4]),
        )
