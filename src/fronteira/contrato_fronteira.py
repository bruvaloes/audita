"""Fronteira CLI para gerenciamento de contratos (RF 04 a RF 08)."""
from functools import wraps
from typing import TYPE_CHECKING
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.sessao import Sessao
from controle.utils.datas import formatar_data
from entidade.usuario import Usuario
from excecao.acesso_negado_error import AcessoNegadoError
from excecao.persistencia_error import PersistenciaError
from excecao.validacao_error import ValidacaoError

if TYPE_CHECKING:
    from controle.facade_singleton_controller import FacadeSingletonController

LARGURA_TABELA = 85


def _mostrando_acesso_negado(acao):
    """Exibe `Acesso negado` em vez de deixar o erro encerrar o programa."""
    @wraps(acao)
    def executar(self):
        try:
            acao(self)
        except AcessoNegadoError as erro:
            print(f"\n{erro}")
    return executar


class ContratoFronteira:
    """Interface de usuário no terminal para operações de contrato."""

    def __init__(self, controller: "FacadeSingletonController | ContratoController", sessao: Sessao):
        self._controller = controller
        self._sessao = sessao


    @property
    def _solicitante(self) -> Usuario | None:
        return self._sessao.usuario_atual

    @_mostrando_acesso_negado
    def cadastrar_contrato(self) -> None:
        print("\n--- Cadastro de Contrato ---")
        numero = input("Número do contrato (até 20 caracteres): ").strip()
        empresa = input("Empresa contratada: ").strip()
        inicio = input("Vigência início (dd/mm/aaaa): ").strip()
        fim = input("Vigência fim (dd/mm/aaaa): ").strip()
        arquivo = input("Caminho do arquivo (PDF ou DOCX até 30 MB, opcional): ").strip()
        arquivo = arquivo if arquivo else None

        dados = DadosCadastroContrato(
            numero=numero,
            empresa_contratada=empresa,
            vigencia_inicio=inicio,
            vigencia_fim=fim,
            arquivo=arquivo,
        )

        try:
            contrato = self._controller.adicionar(
                self._solicitante,
                dados
            )
            print("\nContrato cadastrado com sucesso!")
            print(f"   {contrato}")
        except ValidacaoError as erro:
            print(f"\nErro ao cadastrar contrato: {erro}")
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")

    @_mostrando_acesso_negado
    def listar_contratos(self) -> None:
        print("\n--- Listagem de Contratos ---")
        busca = input("Termo de busca por número ou empresa (ou Enter para todos): ").strip()
        busca = busca if busca else None

        situacao = input("Filtro de situação (ATIVO, ENCERRADO ou Enter para todos): ").strip()
        situacao = situacao if situacao else None

        pagina = 1
        while True:
            try:
                resultado = self._controller.listar(
                    self._solicitante,
                    busca=busca,
                    situacao=situacao,
                    pagina=pagina,
                    por_pagina=20,
                )
            except PersistenciaError as erro:
                print(f"\nErro de armazenamento: {erro}")
                return

            if resultado.total_itens == 0:
                print("\nNenhum contrato encontrado.")
                return

            self._exibir_tabela(resultado.itens, resultado.pagina_atual, resultado.total_paginas, resultado.total_itens)

            if resultado.total_paginas <= 1:
                break

            print("\nNavegação de páginas:")
            print("P - Próxima página" if pagina < resultado.total_paginas else "")
            print("A - Página anterior" if pagina > 1 else "")
            print("V - Voltar ao menu")
            escolha = input("Escolha uma opção de navegação: ").strip().upper()

            if escolha == "P" and pagina < resultado.total_paginas:
                pagina += 1
            elif escolha == "A" and pagina > 1:
                pagina -= 1
            else:
                break

    @_mostrando_acesso_negado
    def editar_contrato(self) -> None:
        print("\n--- Edição de Contrato ---")
        numero_atual = input("Número do contrato que deseja editar: ").strip()
        contrato = self._controller.buscar_por_numero(self._solicitante, numero_atual)
        if not contrato:
            print(f"\nContrato '{numero_atual}' não encontrado.")
            return

        print(f"Editando: {contrato}")
        print("(Pressione Enter para manter o valor atual entre colchetes)")

        novo_numero = input(f"Novo número [{contrato.numero}]: ").strip()
        novo_numero = novo_numero if novo_numero else contrato.numero

        nova_empresa = input(f"Nova empresa contratada [{contrato.empresa_contratada}]: ").strip()
        nova_empresa = nova_empresa if nova_empresa else contrato.empresa_contratada

        inicio_str = formatar_data(contrato.vigencia_inicio)
        novo_inicio = input(f"Nova vigência início [{inicio_str}]: ").strip()
        novo_inicio = novo_inicio if novo_inicio else inicio_str

        fim_str = formatar_data(contrato.vigencia_fim)
        novo_fim = input(f"Nova vigência fim [{fim_str}]: ").strip()
        novo_fim = novo_fim if novo_fim else fim_str

        arquivo_atual = contrato.arquivo or "Nenhum"
        novo_arquivo = input(f"Novo arquivo [{arquivo_atual}]: ").strip()
        arquivo_final = novo_arquivo if novo_arquivo else contrato.arquivo

        dados = DadosCadastroContrato(
            numero=novo_numero,
            empresa_contratada=nova_empresa,
            vigencia_inicio=novo_inicio,
            vigencia_fim=novo_fim,
            arquivo=arquivo_final,
        )

        try:
            atualizado = self._controller.atualizar(
                self._solicitante,
                numero_atual,
                dados
            )
            print("\nContrato atualizado com sucesso!")
            print(f"   {atualizado}")
        except ValidacaoError as erro:
            print(f"\nErro ao editar contrato: {erro}")
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")

    @_mostrando_acesso_negado
    def encerrar_contrato(self) -> None:
        print("\n--- Encerramento de Contrato ---")
        numero = input("Número do contrato a encerrar: ").strip()
        contrato = self._controller.buscar_por_numero(self._solicitante, numero)
        if not contrato:
            print(f"\nContrato '{numero}' não encontrado.")
            return

        confirmar = input(f"Confirma o encerramento do contrato {numero}? (s/n): ").strip().lower()
        if confirmar not in ("s", "sim"):
            print("Encerramento cancelado.")
            return

        try:
            encerrado = self._controller.encerrar(
                self._solicitante,
                numero
            )
            print(f"\nContrato {numero} encerrado com sucesso!")
            print(f"   {encerrado}")
        except ValidacaoError as erro:
            print(f"\nErro ao encerrar contrato: {erro}")
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")

    @_mostrando_acesso_negado
    def remover_contrato(self) -> None:
        print("\n--- Remoção de Contrato ---")
        numero = input("Número do contrato que deseja remover: ").strip()
        contrato = self._controller.buscar_por_numero(self._solicitante, numero)
        if not contrato:
            print(f"\nContrato '{numero}' não encontrado.")
            return

        confirmacao = input(
            f"Atenção: deseja realmente remover o contrato {numero}? Esta ação não pode ser desfeita (s/n): "
        ).strip().lower()
        confirmado = confirmacao in ("s", "sim")

        try:
            removido = self._controller.remover(
                self._solicitante,
                numero,
                confirmado=confirmado
            )
            if removido:
                print(f"\nContrato {numero} removido com sucesso!")
            else:
                print("\nRemoção cancelada pelo usuário. O contrato permanece inalterado.")
        except ValidacaoError as erro:
            print(f"\nNão foi possível remover o contrato: {erro}")
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")

    @_mostrando_acesso_negado
    def vincular_usuario(self) -> None:
        print("\n--- Vincular Usuário ao Contrato ---")
        numero = input("Número do contrato: ").strip()
        id_str = input("ID do usuário a vincular (fiscal ou funcionário): ").strip()
        if not id_str.isdigit():
            print("ID inválido. Informe um número inteiro.")
            return

        try:
            self._controller.vincular(
                self._solicitante,
                numero,
                int(id_str)
            )
            print(f"\nUsuário {id_str} vinculado ao contrato {numero} com sucesso!")
        except ValidacaoError as erro:
            print(f"\nErro ao vincular usuário: {erro}")
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")

    @_mostrando_acesso_negado
    def desvincular_usuario(self) -> None:
        print("\n--- Desvincular Usuário do Contrato ---")
        numero = input("Número do contrato: ").strip()
        id_str = input("ID do usuário a desvincular: ").strip()
        if not id_str.isdigit():
            print("ID inválido. Informe um número inteiro.")
            return

        try:
            self._controller.desvincular(
                self._solicitante,
                numero,
                int(id_str)
            )
            print(f"\nUsuário {id_str} desvinculado do contrato {numero} com sucesso!")
        except ValidacaoError as erro:
            print(f"\nErro ao desvincular usuário: {erro}")
        except PersistenciaError as erro:
            print(f"\nErro de armazenamento: {erro}")

    def _exibir_tabela(
        self,
        contratos: list,
        pagina_atual: int,
        total_paginas: int,
        total_itens: int,
    ) -> None:
        print(f"\n{'Número':<18} {'Empresa':<28} {'Vigência':<25} {'Situação':<10}")
        print("-" * LARGURA_TABELA)
        for c in contratos:
            inicio = formatar_data(c.vigencia_inicio)
            fim = formatar_data(c.vigencia_fim)
            vigencia = f"{inicio} até {fim}"
            print(f"{c.numero:<18} {c.empresa_contratada[:26]:<28} {vigencia:<25} {c.situacao.value:<10}")
        print(f"\nTotal: {total_itens} contrato(s) | Página {pagina_atual} de {total_paginas}")
