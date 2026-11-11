"""Compatibilidade temporária: interfaces foram movidas para negocio."""
from negocio.contrato_repositorio import (
    ConsultaContratos,
    PersistenciaContratos,
    ContratoRepositorio,
)

__all__ = ["ConsultaContratos", "PersistenciaContratos", "ContratoRepositorio"]
