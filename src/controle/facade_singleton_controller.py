"""Fachada única com os padrões Facade e Singleton (Issue #19).

Centraliza o acesso das camadas de fronteira às operações de negócio
(usuários, autenticação e contratos) e garante uma instância única
para coordenação dos controladores e contagem global de entidades.
"""
from typing import ClassVar

from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController, ResultadoPaginado
from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.usuario_controller import UsuarioController
from entidade.contrato import Contrato
from entidade.situacao_contrato import SituacaoContrato
from entidade.usuario import Usuario
from persistencia.evidencia_repositorio import EvidenciaRepositorio


class FacadeSingletonController:
    """Fachada única do sistema implementada com o padrão Singleton.

    Concentra os controladores de negócio (UsuarioController, AutenticacaoController
    e ContratoController), provendo um ponto único de entrada para a camada de
    fronteira e garantindo uma única instância ativa.
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
    ) -> None:
        # Permite reinicializar ou atualizar dependências quando explicitamente fornecidas
        if not getattr(self, "_inicializado", False) or usuario_controller is not None:
            if usuario_controller is not None:
                self._usuario_controller = usuario_controller
            if autenticacao_controller is not None:
                self._autenticacao_controller = autenticacao_controller
            if contrato_controller is not None:
                self._contrato_controller = contrato_controller
            if evidencia_repositorio is not None:
                self._evidencia_repositorio = evidencia_repositorio
            elif (
                hasattr(self, "_contrato_controller")
                and getattr(self._contrato_controller, "_evidencia_repositorio", None) is not None
            ):
                self._evidencia_repositorio = self._contrato_controller._evidencia_repositorio
            else:
                if not hasattr(self, "_evidencia_repositorio"):
                    self._evidencia_repositorio = None

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

    # =========================================================================
    # Operações de Autenticação (RF 02 / #56)
    # =========================================================================

    def autenticar(self, identificador: str, senha: str, perfil: str) -> Usuario:
        """Autentica o usuário pelo identificador, senha e perfil informado."""
        return self._autenticacao_controller.autenticar(
            identificador=identificador, senha=senha, perfil=perfil
        )

    # =========================================================================
    # Operações de Usuários (RF 01)
    # =========================================================================

    def adicionar_usuario(self, dados: DadosCadastroUsuario) -> Usuario:
        """Cadastra um novo usuário no sistema."""
        return self._usuario_controller.adicionar(dados)

    def listar_usuarios(self) -> list[Usuario]:
        """Lista todos os usuários cadastrados."""
        return self._usuario_controller.listar_todos()

    # Métodos compatíveis com a interface de UsuarioController (duck typing)
    def adicionar(self, dados: DadosCadastroUsuario) -> Usuario:
        """Alias para adicionar_usuario, compatível com UsuarioController."""
        return self.adicionar_usuario(dados)

    def listar_todos(self) -> list[Usuario]:
        """Alias para listar_usuarios, compatível com UsuarioController."""
        return self.listar_usuarios()

    # =========================================================================
    # Operações de Contratos (RF 04 a RF 08 / #65 a #70)
    # =========================================================================

    def adicionar_contrato(
        self,
        dados: DadosCadastroContrato,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Cadastra um novo contrato ativo (RF 04)."""
        return self._contrato_controller.adicionar(dados, usuario_logado=usuario_logado)

    def listar_contratos(
        self,
        busca: str | None = None,
        situacao: str | SituacaoContrato | None = None,
        pagina: int = 1,
        por_pagina: int = 20,
        id_usuario: int | None = None,
    ) -> ResultadoPaginado:
        """Lista contratos com filtro, busca e paginação (RF 05 e RF 08)."""
        return self._contrato_controller.listar(
            busca=busca,
            situacao=situacao,
            pagina=pagina,
            por_pagina=por_pagina,
            id_usuario=id_usuario,
        )

    def buscar_contrato_por_numero(self, numero: str) -> Contrato | None:
        """Busca um contrato pelo seu número identificador."""
        return self._contrato_controller.buscar_por_numero(numero)

    def atualizar_contrato(
        self,
        numero_atual: str,
        dados: DadosCadastroContrato,
        nova_situacao: SituacaoContrato | str | None = None,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Atualiza dados cadastrais ou situação de um contrato existente (RF 06)."""
        return self._contrato_controller.atualizar(
            numero_atual=numero_atual,
            dados=dados,
            nova_situacao=nova_situacao,
            usuario_logado=usuario_logado,
        )

    def encerrar_contrato(
        self,
        numero: str,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Encerra um contrato alterando a situação para ENCERRADO (RF 06)."""
        return self._contrato_controller.encerrar(numero, usuario_logado=usuario_logado)

    def validar_recebimento_evidencia(self, numero: str) -> None:
        """Valida se o contrato está ativo para receber evidências (RN06.2)."""
        return self._contrato_controller.validar_recebimento_evidencia(numero)

    def remover_contrato(
        self,
        numero: str,
        confirmado: bool = False,
        usuario_logado: str | None = None,
    ) -> bool:
        """Remove contrato sem evidências vinculadas após confirmação (RF 07)."""
        return self._contrato_controller.remover(
            numero=numero,
            confirmado=confirmado,
            usuario_logado=usuario_logado,
        )

    def vincular_usuario_contrato(
        self,
        numero: str,
        id_usuario: int,
        usuario_logado: str | None = None,
    ) -> None:
        """Vincula um fiscal ou funcionário a um contrato (RF 08)."""
        return self._contrato_controller.vincular(
            numero=numero,
            id_usuario=id_usuario,
            usuario_logado=usuario_logado,
        )

    def desvincular_usuario_contrato(
        self,
        numero: str,
        id_usuario: int,
        usuario_logado: str | None = None,
    ) -> None:
        """Desvincula um usuário de um contrato respeitando as regras de fiscais (RF 08)."""
        return self._contrato_controller.desvincular(
            numero=numero,
            id_usuario=id_usuario,
            usuario_logado=usuario_logado,
        )

    # Métodos compatíveis com a interface de ContratoController (duck typing)
    def listar(
        self,
        busca: str | None = None,
        situacao: str | SituacaoContrato | None = None,
        pagina: int = 1,
        por_pagina: int = 20,
        id_usuario: int | None = None,
    ) -> ResultadoPaginado:
        """Alias para listar_contratos, compatível com ContratoController."""
        return self.listar_contratos(
            busca=busca,
            situacao=situacao,
            pagina=pagina,
            por_pagina=por_pagina,
            id_usuario=id_usuario,
        )

    def buscar_por_numero(self, numero: str) -> Contrato | None:
        """Alias para buscar_contrato_por_numero, compatível com ContratoController."""
        return self.buscar_contrato_por_numero(numero)

    def atualizar(
        self,
        numero_atual: str,
        dados: DadosCadastroContrato,
        nova_situacao: SituacaoContrato | str | None = None,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Alias para atualizar_contrato, compatível com ContratoController."""
        return self.atualizar_contrato(
            numero_atual=numero_atual,
            dados=dados,
            nova_situacao=nova_situacao,
            usuario_logado=usuario_logado,
        )

    def encerrar(
        self,
        numero: str,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Alias para encerrar_contrato, compatível com ContratoController."""
        return self.encerrar_contrato(numero, usuario_logado=usuario_logado)

    def remover(
        self,
        numero: str,
        confirmado: bool = False,
        usuario_logado: str | None = None,
    ) -> bool:
        """Alias para remover_contrato, compatível com ContratoController."""
        return self.remover_contrato(
            numero=numero,
            confirmado=confirmado,
            usuario_logado=usuario_logado,
        )

    def vincular(
        self,
        numero: str,
        id_usuario: int,
        usuario_logado: str | None = None,
    ) -> None:
        """Alias para vincular_usuario_contrato, compatível com ContratoController."""
        return self.vincular_usuario_contrato(
            numero=numero,
            id_usuario=id_usuario,
            usuario_logado=usuario_logado,
        )

    def desvincular(
        self,
        numero: str,
        id_usuario: int,
        usuario_logado: str | None = None,
    ) -> None:
        """Alias para desvincular_usuario_contrato, compatível com ContratoController."""
        return self.desvincular_usuario_contrato(
            numero=numero,
            id_usuario=id_usuario,
            usuario_logado=usuario_logado,
        )

    # =========================================================================
    # Contagem de Entidades (Issue #19)
    # =========================================================================

    def contar_entidades(self) -> int:
        """Retorna a quantidade total de entidades cadastradas no sistema.

        Soma os usuários cadastrados, os contratos cadastrados (#64)
        e as evidências cadastradas (#68), conforme especificação da issue #19.
        """
        total_usuarios = len(self._usuario_controller.listar_todos())
        total_contratos = self._contrato_controller.listar(por_pagina=1).total_itens
        total_evidencias = 0
        if self._evidencia_repositorio is not None:
            total_evidencias = len(self._evidencia_repositorio.listar())
        return total_usuarios + total_contratos + total_evidencias

    def quantidade_entidades_cadastradas(self) -> int:
        """Alias para contar_entidades."""
        return self.contar_entidades()

    def contar_entidades_detalhado(self) -> dict[str, int]:
        """Retorna o detalhamento das quantidades de entidades cadastradas."""
        total_usuarios = len(self._usuario_controller.listar_todos())
        total_contratos = self._contrato_controller.listar(por_pagina=1).total_itens
        total_evidencias = 0
        if self._evidencia_repositorio is not None:
            total_evidencias = len(self._evidencia_repositorio.listar())
        return {
            "usuarios": total_usuarios,
            "contratos": total_contratos,
            "evidencias": total_evidencias,
            "total": total_usuarios + total_contratos + total_evidencias,
        }
