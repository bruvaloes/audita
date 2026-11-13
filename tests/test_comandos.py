"""Padrão Command (Issue #25): o executor e cada comando concreto da fachada.

Cada comando guarda o receptor e os dados do pedido, e só chama o receptor
quando é executado.
"""
from unittest.mock import MagicMock

import pytest

from controle.autenticacao_controller import AutenticacaoController
from controle.comando.atualizar_contrato_comando import AtualizarContratoComando
from controle.comando.autenticar_comando import AutenticarComando, Credenciais
from controle.comando.buscar_contrato_comando import BuscarContratoComando
from controle.comando.cadastrar_contrato_comando import CadastrarContratoComando
from controle.comando.cadastrar_usuario_comando import CadastrarUsuarioComando
from controle.comando.comando import Comando
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
from controle.contrato_controller import (
    ITENS_POR_PAGINA,
    ContratoController,
    ResultadoPaginado,
)
from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.filtro_contratos import FiltroContratos
from controle.relatorio_controller import RelatorioController
from controle.usuario_controller import UsuarioController
from entidade.contrato import Contrato
from entidade.situacao_contrato import SituacaoContrato
from entidade.usuario import Usuario
from negocio.evidencia_repositorio import EvidenciaRepositorio


@pytest.fixture
def usuarios():
    return MagicMock(spec=UsuarioController)


@pytest.fixture
def contratos():
    return MagicMock(spec=ContratoController)


@pytest.fixture
def solicitante():
    return MagicMock(spec=Usuario)


# --- Executor (invocador) ----------------------------------------------------

class ComandoFixo(Comando[str]):
    def __init__(self, resultado: str):
        self.resultado = resultado
        self.execucoes = 0

    def executar(self) -> str:
        self.execucoes += 1
        return self.resultado


def test_executor_deve_executar_o_comando_e_devolver_o_resultado():
    comando = ComandoFixo("feito")

    resultado = ExecutorComandos().executar(comando)

    assert resultado == "feito"
    assert comando.execucoes == 1


def test_executor_deve_deixar_o_erro_do_receptor_chegar_a_quem_pediu(
        contratos, solicitante):
    contratos.encerrar.side_effect = ValueError("falhou")

    with pytest.raises(ValueError, match="falhou"):
        ExecutorComandos().executar(
            EncerrarContratoComando(contratos, solicitante, "CT-1"))


def test_comando_nao_deve_chamar_o_receptor_antes_de_ser_executado(
        contratos, solicitante):
    EncerrarContratoComando(contratos, solicitante, "CT-1")

    contratos.encerrar.assert_not_called()


def test_comando_deve_ser_abstrato():
    with pytest.raises(TypeError):
        Comando()


# --- Autenticação e usuários -------------------------------------------------

def test_autenticar_comando_deve_autenticar_com_as_credenciais():
    autenticacao = MagicMock(spec=AutenticacaoController)
    usuario = MagicMock(spec=Usuario)
    autenticacao.autenticar.return_value = usuario

    resultado = AutenticarComando(
        autenticacao, Credenciais("maria", "Senha@123", "GESTOR")).executar()

    autenticacao.autenticar.assert_called_once_with(
        identificador="maria", senha="Senha@123", perfil="GESTOR")
    assert resultado is usuario


def test_cadastrar_usuario_comando_deve_adicionar_o_usuario(usuarios):
    dados = MagicMock(spec=DadosCadastroUsuario)
    usuario = MagicMock(spec=Usuario)
    usuarios.adicionar.return_value = usuario

    resultado = CadastrarUsuarioComando(usuarios, dados).executar()

    usuarios.adicionar.assert_called_once_with(dados)
    assert resultado is usuario


def test_listar_usuarios_comando_deve_listar_para_o_solicitante(
        usuarios, solicitante):
    lista = [MagicMock(spec=Usuario)]
    usuarios.listar_todos.return_value = lista

    resultado = ListarUsuariosComando(usuarios, solicitante).executar()

    usuarios.listar_todos.assert_called_once_with(solicitante)
    assert resultado == lista


# --- Contratos ---------------------------------------------------------------

def test_cadastrar_contrato_comando_deve_adicionar_o_contrato(
        contratos, solicitante):
    dados = MagicMock(spec=DadosCadastroContrato)
    contrato = MagicMock(spec=Contrato)
    contratos.adicionar.return_value = contrato

    resultado = CadastrarContratoComando(
        contratos, solicitante, dados).executar()

    contratos.adicionar.assert_called_once_with(solicitante, dados)
    assert resultado is contrato


def test_listar_contratos_comando_deve_repassar_o_filtro(
        contratos, solicitante):
    paginado = ResultadoPaginado([], 2, 3, 25)
    contratos.listar.return_value = paginado
    filtro = FiltroContratos(busca="Alpha", situacao=SituacaoContrato.ATIVO,
                             pagina=2, por_pagina=10, id_usuario=7)

    resultado = ListarContratosComando(
        contratos, solicitante, filtro).executar()

    contratos.listar.assert_called_once_with(
        solicitante, busca="Alpha", situacao=SituacaoContrato.ATIVO,
        pagina=2, por_pagina=10, id_usuario=7)
    assert resultado is paginado


def test_filtro_de_contratos_padrao_deve_ser_a_primeira_pagina_de_todos():
    filtro = FiltroContratos()

    assert (filtro.busca, filtro.situacao, filtro.pagina, filtro.por_pagina,
            filtro.id_usuario) == (None, None, 1, ITENS_POR_PAGINA, None)


def test_buscar_contrato_comando_deve_buscar_pelo_numero(
        contratos, solicitante):
    contrato = MagicMock(spec=Contrato)
    contratos.buscar_por_numero.return_value = contrato

    resultado = BuscarContratoComando(
        contratos, solicitante, "CT-1").executar()

    contratos.buscar_por_numero.assert_called_once_with(solicitante, "CT-1")
    assert resultado is contrato


def test_atualizar_contrato_comando_deve_atualizar_com_os_novos_dados(
        contratos, solicitante):
    dados = MagicMock(spec=DadosCadastroContrato)
    contrato = MagicMock(spec=Contrato)
    contratos.atualizar.return_value = contrato

    resultado = AtualizarContratoComando(
        contratos, solicitante, AtualizacaoContrato("CT-1", dados)).executar()

    contratos.atualizar.assert_called_once_with(
        solicitante, numero_atual="CT-1", dados=dados)
    assert resultado is contrato


def test_encerrar_contrato_comando_deve_encerrar_o_contrato(
        contratos, solicitante):
    contrato = MagicMock(spec=Contrato)
    contratos.encerrar.return_value = contrato

    resultado = EncerrarContratoComando(
        contratos, solicitante, "CT-1").executar()

    contratos.encerrar.assert_called_once_with(solicitante, "CT-1")
    assert resultado is contrato


@pytest.mark.parametrize("confirmado", [True, False])
def test_remover_contrato_comando_deve_repassar_a_confirmacao(
        contratos, solicitante, confirmado):
    contratos.remover.return_value = confirmado

    removido = RemoverContratoComando(
        contratos, solicitante,
        RemocaoContrato("CT-1", confirmado)).executar()

    contratos.remover.assert_called_once_with(
        solicitante=solicitante, numero="CT-1", confirmado=confirmado)
    assert removido is confirmado


def test_remocao_de_contrato_sem_confirmacao_deve_ser_o_padrao():
    assert RemocaoContrato("CT-1").confirmado is False


def test_vincular_usuario_contrato_comando_deve_vincular_o_usuario(
        contratos, solicitante):
    VincularUsuarioContratoComando(
        contratos, solicitante, VinculoContrato("CT-1", 10)).executar()

    contratos.vincular.assert_called_once_with(
        solicitante=solicitante, numero="CT-1", id_usuario=10)


def test_desvincular_usuario_contrato_comando_deve_desvincular_o_usuario(
        contratos, solicitante):
    DesvincularUsuarioContratoComando(
        contratos, solicitante, VinculoContrato("CT-1", 10)).executar()

    contratos.desvincular.assert_called_once_with(
        solicitante=solicitante, numero="CT-1", id_usuario=10)


def test_validar_recebimento_evidencia_comando_deve_validar_o_contrato(
        contratos):
    ValidarRecebimentoEvidenciaComando(contratos, "CT-1").executar()

    contratos.validar_recebimento_evidencia.assert_called_once_with("CT-1")


# --- Relatório e contagem ----------------------------------------------------

def test_gerar_relatorio_acessos_comando_deve_devolver_o_caminho(
        solicitante, tmp_path):
    relatorios = MagicMock(spec=RelatorioController)
    relatorios.gerar_relatorio_acessos.return_value = tmp_path / "r.pdf"

    caminho = GerarRelatorioAcessosComando(relatorios, solicitante).executar()

    relatorios.gerar_relatorio_acessos.assert_called_once_with(solicitante)
    assert caminho == tmp_path / "r.pdf"


def test_contar_entidades_comando_deve_somar_as_tres_entidades(
        usuarios, contratos):
    evidencias = MagicMock(spec=EvidenciaRepositorio)
    usuarios.contar.return_value = 3
    contratos.contar.return_value = 4
    evidencias.listar.return_value = [MagicMock(), MagicMock()]

    quantidade = ContarEntidadesComando(
        usuarios, contratos, evidencias).executar()

    assert quantidade == {
        "usuarios": 3, "contratos": 4, "evidencias": 2, "total": 9}


def test_contar_entidades_comando_sem_evidencias_deve_contar_zero(
        usuarios, contratos):
    usuarios.contar.return_value = 1
    contratos.contar.return_value = 2

    quantidade = ContarEntidadesComando(usuarios, contratos, None).executar()

    assert quantidade["evidencias"] == 0
    assert quantidade["total"] == 3
