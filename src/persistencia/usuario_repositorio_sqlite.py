"""Compatibilidade temporária: implementação foi movida para infraestrutura."""
from infraestrutura.usuario_repositorio_sqlite import (
    COLUNAS_USUARIO,
    UsuarioRepositorioSQLite,
)

__all__ = ["COLUNAS_USUARIO", "UsuarioRepositorioSQLite"]
