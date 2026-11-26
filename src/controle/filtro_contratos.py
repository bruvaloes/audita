from dataclasses import dataclass

from controle.contrato_controller import ITENS_POR_PAGINA
from entidade.situacao_contrato import SituacaoContrato


@dataclass(frozen=True)
class FiltroContratos:
    """Busca, filtro de situação e página da listagem de contratos (RF 05 e
    RF 08)."""
    busca: str | None = None
    situacao: str | SituacaoContrato | None = None
    pagina: int = 1
    por_pagina: int = ITENS_POR_PAGINA
    id_usuario: int | None = None
