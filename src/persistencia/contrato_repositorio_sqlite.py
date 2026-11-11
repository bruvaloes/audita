"""Compatibilidade temporária: implementação foi movida para infraestrutura."""
from infraestrutura.contrato_repositorio_sqlite import (
    COLUNAS_CONTRATO,
    ContratoRepositorioSQLite,
)

__all__ = ["COLUNAS_CONTRATO", "ContratoRepositorioSQLite"]
