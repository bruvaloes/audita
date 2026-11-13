from controle.comando.comando import Comando
from controle.contrato_controller import ContratoController, ResultadoPaginado
from controle.filtro_contratos import FiltroContratos
from entidade.usuario import Usuario


class ListarContratosComando(Comando[ResultadoPaginado]):
    """Lista contratos com filtro, busca e paginação (RF 05 e RF 08)."""

    def __init__(self, contratos: ContratoController,
                 solicitante: Usuario | None, filtro: FiltroContratos):
        self._contratos = contratos
        self._solicitante = solicitante
        self._filtro = filtro

    def executar(self) -> ResultadoPaginado:
        return self._contratos.listar(
            self._solicitante,
            busca=self._filtro.busca,
            situacao=self._filtro.situacao,
            pagina=self._filtro.pagina,
            por_pagina=self._filtro.por_pagina,
            id_usuario=self._filtro.id_usuario,
        )
