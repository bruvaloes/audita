"""Fachada única com os padrões Facade, Singleton (Issue #19) e Command
(Issue #25).

Centraliza o acesso das camadas de fronteira às operações de negócio
(usuários, autenticação, contratos e relatórios) e garante uma instância única
para coordenação dos controladores e contagem global de entidades. Cada
operação é montada como um comando e executada pelo `ExecutorComandos`; os
controllers são os receptores e continuam conferindo as permissões.
"""
from pathlib import Path
from typing import ClassVar

from controle.autenticacao_controller import AutenticacaoController
from controle.comando.atualizar_contrato_comando import AtualizarContratoComando
from controle.comando.autenticar_comando import AutenticarComando, Credenciais
from controle.comando.buscar_contrato_comando import BuscarContratoComando
from controle.comando.cadastrar_contrato_comando import CadastrarContratoComando
from controle.comando.cadastrar_usuario_comando import CadastrarUsuarioComando
from controle.comando.contar_entidades_comando import ContarEntidadesComando
from controle.comando.dados_comando_contrato import (
    AtualizacaoContrato,
    RemocaoContrato,
    VinculoContrato,
)
from controle.comando.desvincular_usuario_contrato_comando import (
    DesvincularUsuarioContratoComando,
)
from controle.comando.encerrar_contrato_comando import EncerrarContratoComando
from controle.comando.executor_comandos import ExecutorComandos
from controle.comando.gerar_relatorio_acessos_comando import (
    GerarRelatorioAcessosComando,
)
from controle.comando.listar_contratos_comando import ListarContratosComando
from controle.comando.listar_usuarios_comando import ListarUsuariosComando
from controle.comando.remover_contrato_comando import RemoverContratoComando
from controle.comando.validar_recebimento_evidencia_comando import (
    ValidarRecebimentoEvidenciaComando,
)
from controle.comando.vincular_usuario_contrato_comando import (
    VincularUsuarioContratoComando,
)
from controle.contrato_controller import ContratoController, ResultadoPaginado
from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.filtro_contratos import FiltroContratos
from controle.relatorio_controller import RelatorioController
from controle.usuario_controller import UsuarioController
from entidade.contrato import Contrato
from entidade.usuario import Usuario
from negocio.evidencia_repositorio import EvidenciaRepositorio


class FacadeSingletonController:
    """Fachada única do sistema implementada com o padrão Singleton.

    Concentra os controladores de negócio (UsuarioController, AutenticacaoController,
    ContratoController e RelatorioController), provendo um ponto único de entrada para a camada de
    fronteira e garantindo uma única instância ativa. É o cliente do padrão
    Command: cada método só monta o comando da operação e o entrega ao
    executor, sem regra de negócio própria.
    """

    _instancia: ClassVar["FacadeSingletonController | None"] = None

    def __new__(cls, *args, **kwargs) -> "FacadeSingletonController":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(
        self,
        usuario_controller: UsuarioController | None = None,
        autenticacao_controller: AutenticacaoController | None = None,
        contrato_controller: ContratoController | None = None,
        evidencia_repositorio: EvidenciaRepositorio | None = None,
        relatorio_controller: RelatorioController | None = None,
    ) -> None:
        if not getattr(self, "_inicializado", False) or usuario_controller is not None:
            if usuario_controller is not None:
                self._usuario_controller = usuario_controller
            if autenticacao_controller is not None:
                self._autenticacao_controller = autenticacao_controller
            if contrato_controller is not None:
                self._contrato_controller = contrato_controller
            if evidencia_repositorio is not None:
                self._evidencia_repositorio = evidencia_repositorio
            elif not hasattr(self, "_evidencia_repositorio"):
                self._evidencia_repositorio = None
            if relatorio_controller is not None:
                self._relatorio_controller = relatorio_controller
            if not hasattr(self, "_executor"):
                self._executor = ExecutorComandos()

            self._inicializado = True

    @classmethod
    def obter_instancia(cls) -> "FacadeSingletonController":
        """Retorna a instância única da fachada.

        Levanta RuntimeError caso a fachada ainda não tenha sido instanciada.
        """
        if cls._instancia is None:
            raise RuntimeError("FacadeSingletonController ainda não foi instanciada.")
        return cls._instancia

    @classmethod
    def resetar_instancia(cls) -> None:
        """Reseta a instância única da fachada.

        Útil para garantir isolamento e independência entre testes automatizados.
        """
        cls._instancia = None

    # Propriedades de acesso aos controllers
    @property
    def usuario_controller(self) -> UsuarioController:
        return self._usuario_controller

    @property
    def autenticacao_controller(self) -> AutenticacaoController:
        return self._autenticacao_controller

    @property
    def contrato_controller(self) -> ContratoController:
        return self._contrato_controller

    @property
    def evidencia_repositorio(self) -> EvidenciaRepositorio | None:
        return self._evidencia_repositorio

    @property
    def relatorio_controller(self) -> RelatorioController:
        return self._relatorio_controller

    @property
    def executor(self) -> ExecutorComandos:
        return self._executor

    # =========================================================================
    # Operações de Autenticação (RF 02 / #56)
    # =========================================================================

    def autenticar(self, identificador: str, senha: str, perfil: str) -> Usuario:
        """Autentica o usuário pelo identificador, senha e perfil informado."""
        return self._executor.executar(AutenticarComando(
            self._autenticacao_controller,
            Credenciais(identificador, senha, perfil),
        ))

    # =========================================================================
    # Operações de Usuários (RF 01)
    # =========================================================================

    def adicionar_usuario(self, dados: DadosCadastroUsuario) -> Usuario:
        """Cadastra um novo usuário no sistema."""
        return self._executor.executar(
            CadastrarUsuarioComando(self._usuario_controller, dados))

    def listar_usuarios(self, solicitante: Usuario | None = None) -> list[Usuario]:
        """Lista todos os usuários cadastrados."""
        return self._executor.executar(
            ListarUsuariosComando(self._usuario_controller, solicitante))

    # =========================================================================
    # Operações de Contratos (RF 04 a RF 08 / #65 a #70)
    # =========================================================================

    def adicionar_contrato(
        self,
        solicitante: Usuario | None,
        dados: DadosCadastroContrato,
    ) -> Contrato:
        """Cadastra um novo contrato ativo (RF 04)."""
        return self._executor.executar(CadastrarContratoComando(
            self._contrato_controller, solicitante, dados))

    def listar_contratos(
        self,
        solicitante: Usuario | None,
        filtro: FiltroContratos | None = None,
    ) -> ResultadoPaginado:
        """Lista contratos com filtro, busca e paginação (RF 05 e RF 08).

        Sem filtro, lista a primeira página de todos os contratos.
        """
        return self._executor.executar(ListarContratosComando(
            self._contrato_controller, solicitante,
            filtro or FiltroContratos()))

    def buscar_contrato_por_numero(
        self, solicitante: Usuario | None, numero: str
    ) -> Contrato | None:
        """Busca um contrato pelo seu número identificador."""
        return self._executor.executar(BuscarContratoComando(
            self._contrato_controller, solicitante, numero))

    def atualizar_contrato(
        self,
        solicitante: Usuario | None,
        numero_atual: str,
        dados: DadosCadastroContrato,
    ) -> Contrato:
        """Atualiza os dados cadastrais de um contrato existente (RF 06)."""
        return self._executor.executar(AtualizarContratoComando(
            self._contrato_controller, solicitante,
            AtualizacaoContrato(numero_atual, dados)))

    def encerrar_contrato(
        self,
        solicitante: Usuario | None,
        numero: str,
    ) -> Contrato:
        """Encerra um contrato alterando a situação para ENCERRADO (RF 06)."""
        return self._executor.executar(EncerrarContratoComando(
            self._contrato_controller, solicitante, numero))

    def validar_recebimento_evidencia(self, numero: str) -> None:
        """Valida se o contrato está ativo para receber evidências (RN06.2)."""
        return self._executor.executar(ValidarRecebimentoEvidenciaComando(
            self._contrato_controller, numero))

    def remover_contrato(
        self,
        solicitante: Usuario | None,
        numero: str,
        confirmado: bool = False,
    ) -> bool:
        """Remove contrato sem evidências vinculadas após confirmação (RF 07)."""
        return self._executor.executar(RemoverContratoComando(
            self._contrato_controller, solicitante,
            RemocaoContrato(numero, confirmado)))

    def vincular_usuario_contrato(
        self,
        solicitante: Usuario | None,
        numero: str,
        id_usuario: int,
    ) -> None:
        """Vincula um fiscal ou funcionário a um contrato (RF 08)."""
        return self._executor.executar(VincularUsuarioContratoComando(
            self._contrato_controller, solicitante,
            VinculoContrato(numero, id_usuario)))

    def desvincular_usuario_contrato(
        self,
        solicitante: Usuario | None,
        numero: str,
        id_usuario: int,
    ) -> None:
        """Desvincula um usuário de um contrato respeitando as regras de fiscais (RF 08)."""
        return self._executor.executar(DesvincularUsuarioContratoComando(
            self._contrato_controller, solicitante,
            VinculoContrato(numero, id_usuario)))

    # =========================================================================
    # Relatórios (RF 15 / #22)
    # =========================================================================

    def gerar_relatorio_acessos(self, solicitante: Usuario | None) -> Path:
        """Gera o relatório de estatísticas de acesso e devolve onde o
        arquivo foi salvo (RF 15)."""
        return self._executor.executar(GerarRelatorioAcessosComando(
            self._relatorio_controller, solicitante))

    # =========================================================================
    # Contagem de Entidades (Issue #19)
    # =========================================================================

    def contar_entidades(self) -> int:
        """Quantidade total de entidades cadastradas: usuários, contratos e
        evidências (RF 16). É uma contagem agregada, sem dados pessoais, e por
        isso não exige login."""
        return self.contar_entidades_detalhado()["total"]

    def contar_entidades_detalhado(self) -> dict[str, int]:
        """Quantidade de cada tipo de entidade e o total."""
        return self._executor.executar(ContarEntidadesComando(
            self._usuario_controller,
            self._contrato_controller,
            self._evidencia_repositorio,
        ))
