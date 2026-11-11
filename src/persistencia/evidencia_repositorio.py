"""Compatibilidade temporária: interfaces foram movidas para negocio."""
from negocio.evidencia_repositorio import (
    ConsultaEvidencias,
    PersistenciaEvidencias,
    EvidenciaRepositorio,
)

__all__ = [
    "ConsultaEvidencias",
    "PersistenciaEvidencias",
    "EvidenciaRepositorio",
]
