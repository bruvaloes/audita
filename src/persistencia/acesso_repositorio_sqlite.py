"""Compatibilidade temporária: implementação foi movida para infraestrutura."""
from infraestrutura.acesso_repositorio_sqlite import (
    COLUNAS_ACESSO,
    AcessoRepositorioSQLite,
)

__all__ = ["COLUNAS_ACESSO", "AcessoRepositorioSQLite"]
