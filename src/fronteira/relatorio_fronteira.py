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
        formato = self._escolher_formato()
        if formato is None:
            print("\nOpção de formato inválida.")
            return
        try:
            caminho = self._controller.gerar_relatorio_acessos(
                self._sessao.usuario_atual, formato)
        except AcessoNegadoError as erro:
            print(f"\n{erro}")
            return
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")
            return

        print("\nRelatório gerado com sucesso!")
        print(f"Arquivo salvo em: {caminho}")

    def _escolher_formato(self) -> str | None:
        """Mostra os formatos numerados e devolve o escolhido; Enter fica
        com o padrão (o primeiro). Devolve None se a opção for inválida."""
        formatos = self._controller.listar_formatos_relatorio_acessos()
        print("Formatos disponíveis:")
        for numero, formato in enumerate(formatos, start=1):
            print(f"{numero} - {formato.upper()}")
        escolha = input(
            f"Escolha o formato (Enter para {formatos[0].upper()}): ").strip()
        if not escolha:
            return formatos[0]
        if escolha.isascii() and escolha.isdigit() and 1 <= int(escolha) <= len(formatos):
            return formatos[int(escolha) - 1]
        return None
