"""Fronteira CLI dos relatórios do Gestor (RF 15)."""
from typing import TYPE_CHECKING

from controle.sessao import Sessao
from excecao.acesso_negado_error import AcessoNegadoError
from excecao.persistencia_error import PersistenciaError

if TYPE_CHECKING:
    from controle.facade_singleton_controller import FacadeSingletonController


class RelatorioFronteira:
    """Interface de usuário no terminal para a geração de relatórios."""

    def __init__(self, controller: "FacadeSingletonController", sessao: Sessao):
        self._controller = controller
        self._sessao = sessao

    def gerar_relatorio_acessos(self) -> None:
        print("\n--- Relatório de Acessos ---")
        try:
            caminho = self._controller.gerar_relatorio_acessos(
                self._sessao.usuario_atual)
        except AcessoNegadoError as erro:
            print(f"\n{erro}")
            return
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")
            return

        print("\nRelatório gerado com sucesso!")
        print(f"Arquivo salvo em: {caminho}")
