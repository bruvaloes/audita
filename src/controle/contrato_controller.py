from dataclasses import dataclass
from datetime import datetime
import math
from typing import Callable

from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.utils.datas import formatar_data
from controle.validacao.validador_cadastro_contrato import ValidadorCadastroContrato
from controle.validacao.validador_vigencia import ValidadorVigencia
from entidade.contrato import Contrato
from entidade.perfil import Perfil
from entidade.situacao_contrato import SituacaoContrato
from excecao.validacao_error import (
    ContratoComEvidenciasError,
    ContratoNaoEncontradoError,
    ContratoNumeroJaCadastradoError,
    PerfilNaoVinculavelError,
    UltimoFiscalError,
    ValidacaoError,
)
from log.log_auditoria import LogAuditoria
from log.operacao_log import OperacaoLog
from log.registro_log import RegistroLog
from persistencia.contrato_repositorio import ContratoRepositorio
from persistencia.evidencia_repositorio import EvidenciaRepositorio
from persistencia.usuario_repositorio import UsuarioRepositorio


@dataclass
class ResultadoPaginado:
    """Resultado paginado da listagem de contratos."""
    itens: list[Contrato]
    pagina_atual: int
    total_paginas: int
    total_itens: int

    def __iter__(self):
        return iter((self.itens, self.total_paginas))

    def __len__(self):
        return len(self.itens)

    def __getitem__(self, index):
        return self.itens[index]


class ContratoController:
    """Controlador para operações do ciclo de vida de contratos (RF 04 a RF 08)."""

    def __init__(
        self,
        repositorio: ContratoRepositorio,
        evidencia_repositorio: EvidenciaRepositorio | None = None,
        usuario_repositorio: UsuarioRepositorio | None = None,
        relogio: Callable[[], datetime] = datetime.now,
        log: LogAuditoria | None = None,
    ):
        self._repositorio = repositorio
        self._evidencia_repositorio = evidencia_repositorio
        self._usuario_repositorio = usuario_repositorio
        self._relogio = relogio
        self._log = log

    def adicionar(
        self,
        dados: DadosCadastroContrato,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Cadastra um novo contrato ativo após validações (RF 04)."""
        validador = ValidadorCadastroContrato(consulta=self._repositorio)
        inicio, fim = validador.validar(dados)

        contrato = Contrato(
            id=0,
            numero=dados.numero.strip(),
            empresa_contratada=dados.empresa_contratada.strip(),
            vigencia_inicio=inicio,
            vigencia_fim=fim,
            arquivo=dados.arquivo.strip() if dados.arquivo else None,
            situacao=SituacaoContrato.ATIVO,
            usuarios_vinculados=[],
        )
        salvo = self._repositorio.salvar(contrato)

        if self._log:
            self._log.registrar(
                RegistroLog(
                    usuario=usuario_logado,
                    operacao=OperacaoLog.CADASTRO,
                    data_hora=self._relogio(),
                    detalhes=f"Cadastro de contrato: {salvo.numero} ({salvo.empresa_contratada})",
                )
            )
        return salvo

    def listar(
        self,
        busca: str | None = None,
        situacao: str | SituacaoContrato | None = None,
        pagina: int = 1,
        por_pagina: int = 20,
        id_usuario: int | None = None,
    ) -> ResultadoPaginado:
        """Lista contratos com ordenação, busca, filtro por situação, perfil e paginação (RF 05 e RF 08)."""
        contratos = self._repositorio.listar()

        # RN05.2: Ordenação padrão pela vigência início decrescente (mais recente primeiro)
        contratos.sort(key=lambda c: c.vigencia_inicio, reverse=True)

        # RN08.4: Se especificado funcionário, filtra apenas os contratos vinculados a ele
        if id_usuario is not None:
            contratos = [c for c in contratos if id_usuario in c.usuarios_vinculados]

        # RN05.3: Busca por parte do número ou nome da empresa (sem diferenciar maiúsculas)
        if busca and busca.strip():
            termo = busca.strip().lower()
            contratos = [
                c for c in contratos
                if termo in c.numero.lower() or termo in c.empresa_contratada.lower()
            ]

        # RN05.3: Filtro por situação (ATIVO, ENCERRADO ou todos)
        if situacao:
            if isinstance(situacao, str) and situacao.strip().upper() != "TODOS":
                situacao_enum = SituacaoContrato.de_texto(situacao)
                contratos = [c for c in contratos if c.situacao == situacao_enum]
            elif isinstance(situacao, SituacaoContrato):
                contratos = [c for c in contratos if c.situacao == situacao]

        # RN05.4: Paginação
        total_itens = len(contratos)
        total_paginas = math.ceil(total_itens / por_pagina) if total_itens > 0 else 0
        pagina_atual = max(1, pagina)
        inicio_idx = (pagina_atual - 1) * por_pagina
        fim_idx = inicio_idx + por_pagina
        itens = contratos[inicio_idx:fim_idx]

        return ResultadoPaginado(
            itens=itens,
            pagina_atual=pagina_atual,
            total_paginas=total_paginas,
            total_itens=total_itens,
        )

    def buscar_por_numero(self, numero: str) -> Contrato | None:
        """Consulta um contrato pelo número."""
        return self._repositorio.buscar_por_numero(numero)

    def atualizar(
        self,
        numero_atual: str,
        dados: DadosCadastroContrato,
        nova_situacao: SituacaoContrato | str | None = None,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Atualiza os dados de um contrato existente e/ou encerra-o (RF 06)."""
        contrato = self._repositorio.buscar_por_numero(numero_atual)
        if not contrato:
            raise ContratoNaoEncontradoError(f"Contrato '{numero_atual}' não encontrado")

        validador = ValidadorCadastroContrato(
            consulta=self._repositorio, permitir_numero=numero_atual
        )
        inicio, fim = validador.validar(dados)

        novo_numero = dados.numero.strip()
        if novo_numero != numero_atual:
            if self._repositorio.buscar_por_numero(novo_numero) is not None:
                raise ContratoNumeroJaCadastradoError()

        anterior = (
            f"numero={contrato.numero}, empresa={contrato.empresa_contratada}, "
            f"vigencia={contrato.vigencia_inicio} a {contrato.vigencia_fim}, "
            f"situacao={contrato.situacao.value}"
        )

        contrato.empresa_contratada = dados.empresa_contratada.strip()
        contrato.vigencia_inicio = inicio
        contrato.vigencia_fim = fim
        contrato.arquivo = dados.arquivo.strip() if dados.arquivo else None

        if nova_situacao is not None:
            if isinstance(nova_situacao, str):
                contrato.situacao = SituacaoContrato.de_texto(nova_situacao)
            else:
                contrato.situacao = nova_situacao

        if novo_numero != numero_atual:
            self._repositorio.remover(numero_atual)
            contrato.numero = novo_numero
            self._repositorio.salvar(contrato)
        else:
            self._repositorio.atualizar(contrato)

        novo = (
            f"numero={contrato.numero}, empresa={contrato.empresa_contratada}, "
            f"vigencia={contrato.vigencia_inicio} a {contrato.vigencia_fim}, "
            f"situacao={contrato.situacao.value}"
        )

        if self._log:
            self._log.registrar(
                RegistroLog(
                    usuario=usuario_logado,
                    operacao=OperacaoLog.EDICAO,
                    data_hora=self._relogio(),
                    detalhes=f"Contrato {numero_atual} alterado: anterior={{{anterior}}} | novo={{{novo}}}",
                )
            )

        return contrato

    def encerrar(
        self,
        numero: str,
        usuario_logado: str | None = None,
    ) -> Contrato:
        """Encerra um contrato alterando sua situação para ENCERRADO (RF 06)."""
        contrato = self._repositorio.buscar_por_numero(numero)
        if not contrato:
            raise ContratoNaoEncontradoError(f"Contrato '{numero}' não encontrado")

        dados = DadosCadastroContrato(
            numero=contrato.numero,
            empresa_contratada=contrato.empresa_contratada,
            vigencia_inicio=formatar_data(contrato.vigencia_inicio),
            vigencia_fim=formatar_data(contrato.vigencia_fim),
            arquivo=contrato.arquivo,
        )
        return self.atualizar(
            numero,
            dados,
            nova_situacao=SituacaoContrato.ENCERRADO,
            usuario_logado=usuario_logado,
        )

    def validar_recebimento_evidencia(self, numero: str) -> None:
        """Verifica se o contrato pode receber evidências (RN06.2)."""
        contrato = self._repositorio.buscar_por_numero(numero)
        if not contrato:
            raise ContratoNaoEncontradoError(f"Contrato '{numero}' não encontrado")
        if contrato.situacao == SituacaoContrato.ENCERRADO:
            raise ValidacaoError("Contrato encerrado não recebe novas evidências")

    def remover(
        self,
        numero: str,
        confirmado: bool = False,
        usuario_logado: str | None = None,
    ) -> bool:
        """Remove um contrato sem evidências após confirmação explícita (RF 07)."""
        contrato = self._repositorio.buscar_por_numero(numero)
        if not contrato:
            raise ContratoNaoEncontradoError(f"Contrato '{numero}' não encontrado")

        # RN07.1: A remoção exige confirmação explícita
        if not confirmado:
            return False

        # RN07.2: Contrato com ao menos uma evidência não pode ser removido
        if self._evidencia_repositorio is not None:
            evidencias = self._evidencia_repositorio.listar(numero_contrato=numero)
            if len(evidencias) > 0:
                raise ContratoComEvidenciasError()

        # RN07.3: Remove e desfaz vínculos
        self._repositorio.remover(numero)

        if self._log:
            self._log.registrar(
                RegistroLog(
                    usuario=usuario_logado,
                    operacao=OperacaoLog.EXCLUSAO,
                    data_hora=self._relogio(),
                    detalhes=f"Contrato {numero} removido sem evidências vinculadas",
                )
            )
        return True

    def vincular(
        self,
        numero: str,
        id_usuario: int,
        usuario_logado: str | None = None,
    ) -> None:
        """Vincula um fiscal ou funcionário ativo a um contrato (RF 08)."""
        contrato = self._repositorio.buscar_por_numero(numero)
        if not contrato:
            raise ContratoNaoEncontradoError(f"Contrato '{numero}' não encontrado")

        if self._usuario_repositorio is None:
            raise RuntimeError("Repositório de usuários não configurado no ContratoController")

        usuario = next(
            (u for u in self._usuario_repositorio.listar_todos() if u.id == id_usuario),
            None,
        )
        if usuario is None:
            raise ValidacaoError(f"Usuário id={id_usuario} não encontrado")

        # RN08.1: Só usuários ATIVOS com perfil FISCAL ou FUNCIONARIO
        if not usuario.ativo:
            raise ValidacaoError("Usuário inativo não pode ser vinculado a contrato")

        if usuario.perfil not in (Perfil.FISCAL, Perfil.FUNCIONARIO):
            raise PerfilNaoVinculavelError()

        # RN08.3: Um usuário pode estar vinculado a mais de um contrato
        if id_usuario not in contrato.usuarios_vinculados:
            contrato.usuarios_vinculados.append(id_usuario)
            self._repositorio.atualizar(contrato)

    def desvincular(
        self,
        numero: str,
        id_usuario: int,
        usuario_logado: str | None = None,
    ) -> None:
        """Desvincula um usuário de um contrato, respeitando o mínimo de 1 fiscal em contratos ativos (RF 08)."""
        contrato = self._repositorio.buscar_por_numero(numero)
        if not contrato:
            raise ContratoNaoEncontradoError(f"Contrato '{numero}' não encontrado")

        if id_usuario not in contrato.usuarios_vinculados:
            return

        if self._usuario_repositorio is None:
            raise RuntimeError("Repositório de usuários não configurado no ContratoController")

        usuarios_banco = self._usuario_repositorio.listar_todos()
        usuario = next((u for u in usuarios_banco if u.id == id_usuario), None)

        # RN08.2: Contrato ATIVO tem ao menos 1 fiscal; não se desvincula o último
        if (
            contrato.situacao == SituacaoContrato.ATIVO
            and usuario
            and usuario.perfil == Perfil.FISCAL
        ):
            fiscais_vinculados = [
                uid
                for uid in contrato.usuarios_vinculados
                if any(u.id == uid and u.perfil == Perfil.FISCAL for u in usuarios_banco)
            ]
            if len(fiscais_vinculados) <= 1 and id_usuario in fiscais_vinculados:
                raise UltimoFiscalError()

        contrato.usuarios_vinculados.remove(id_usuario)
        self._repositorio.atualizar(contrato)
