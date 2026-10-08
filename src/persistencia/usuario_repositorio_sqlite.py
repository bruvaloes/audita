import sqlite3
from entidade.usuario import Usuario
from entidade.perfil import Perfil
from persistencia.usuario_repositorio import UsuarioRepositorio


class UsuarioRepositorioSQLite(UsuarioRepositorio):
    """Implementação do repositório de usuários utilizando SQLite."""

    def __init__(self, db_name: str = "usuarios.db"):
        self.db_name = db_name
        self._criar_tabela()

    def _conectar(self) -> sqlite3.Connection:
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao conectar ao banco de dados: {e}")

    def _criar_tabela(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT 1
        )
        """
        try:
            with self._conectar() as conn:
                conn.execute(query)
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao criar tabela no banco: {e}")

    def salvar(self, usuario: Usuario) -> Usuario:
        query = """
        INSERT INTO usuarios (nome, cpf, email, login, senha, perfil, ativo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._conectar() as conn:
                cursor = conn.execute(query, (
                    usuario.nome,
                    usuario.cpf,
                    usuario.email,
                    usuario.login,
                    usuario.senha,
                    usuario.perfil.value,
                    usuario.ativo
                ))
                usuario.id = cursor.lastrowid
                return usuario
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao salvar usuário no banco: {e}")

    def listar_todos(self) -> list[Usuario]:
        query = "SELECT id, nome, cpf, email, login, senha, perfil, ativo FROM usuarios"
        usuarios = []
        try:
            with self._conectar() as conn:
                cursor = conn.execute(query)
                for row in cursor.fetchall():
                    usuarios.append(self._montar_usuario(row))
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao listar usuários: {e}")
        return usuarios

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        query = "SELECT id, nome, cpf, email, login, senha, perfil, ativo FROM usuarios WHERE cpf = ?"
        try:
            with self._conectar() as conn:
                cursor = conn.execute(query, (cpf,))
                row = cursor.fetchone()
                if row:
                    return self._montar_usuario(row)
                return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao buscar usuário por CPF: {e}")

    def buscar_por_email(self, email: str) -> Usuario | None:
        query = "SELECT id, nome, cpf, email, login, senha, perfil, ativo FROM usuarios WHERE email = ?"
        try:
            with self._conectar() as conn:
                cursor = conn.execute(query, (email,))
                row = cursor.fetchone()
                if row:
                    return self._montar_usuario(row)
                return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao buscar usuário por E-mail: {e}")

    def _montar_usuario(self, row: tuple) -> Usuario:
        return Usuario(
            id=row[0],
            nome=row[1],
            cpf=row[2],
            email=row[3],
            login=row[4],
            senha=row[5],
            perfil=Perfil(row[6]),
            ativo=bool(row[7])
        )
