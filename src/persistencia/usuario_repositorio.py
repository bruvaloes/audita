"""Compatibilidade temporária: interfaces foram movidas para negocio."""
from negocio.usuario_repositorio import (
    ConsultaUsuarios,
    PersistenciaUsuarios,
    UsuarioRepositorio,
)

__all__ = ["ConsultaUsuarios", "PersistenciaUsuarios", "UsuarioRepositorio"]
