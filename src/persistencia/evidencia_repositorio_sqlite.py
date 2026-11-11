"""Compatibilidade temporária: implementação foi movida para infraestrutura."""
from infraestrutura.evidencia_repositorio_sqlite import (
    COLUNAS_EVIDENCIA,
    EvidenciaRepositorioSQLite,
)

__all__ = ["COLUNAS_EVIDENCIA", "EvidenciaRepositorioSQLite"]
