"""Compatibilidade temporária: interfaces foram movidas para negocio."""
from negocio.acesso_repositorio import (
    ConsultaAcessos,
    PersistenciaAcessos,
    AcessoRepositorio,
)

__all__ = ["ConsultaAcessos", "PersistenciaAcessos", "AcessoRepositorio"]
