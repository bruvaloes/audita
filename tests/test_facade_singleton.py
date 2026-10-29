from unittest.mock import MagicMock
import pytest

from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController, ResultadoPaginado
from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.facade_singleton_controller import FacadeSingletonController
from controle.usuario_controller import UsuarioController
from entidade.contrato import Contrato
from entidade.situacao_contrato import SituacaoContrato
from entidade.usuario import Usuario
from persistencia.evidencia_repositorio import EvidenciaRepositorio


@pytest.fixture(autouse=True)
def limpar_singleton():
    """Garante que cada teste execute com a instância Singleton resetada."""
    FacadeSingletonController.resetar_instancia()
    yield
    FacadeSingletonController.resetar_instancia()


@pytest.fixture
def mock_usuario_controller():
    return MagicMock(spec=UsuarioController)


@pytest.fixture
def mock_autenticacao_controller():
    return MagicMock(spec=AutenticacaoController)


@pytest.fixture
def mock_contrato_controller():
    controller = MagicMock(spec=ContratoController)
    controller.listar.return_value = ResultadoPaginado(
        itens=[],
        pagina_atual=1,
        total_paginas=0,
        total_itens=0,
    )
    return controller


@pytest.fixture
def mock_evidencia_repositorio():
    return MagicMock(spec=EvidenciaRepositorio)


@pytest.fixture
def fachada(
    mock_usuario_controller,
    mock_autenticacao_controller,
    mock_contrato_controller,
    mock_evidencia_repositorio,
):
    return FacadeSingletonController(
        usuario_controller=mock_usuario_controller,
        autenticacao_controller=mock_autenticacao_controller,
        contrato_controller=mock_contrato_controller,
        evidencia_repositorio=mock_evidencia_repositorio,
    )


# =============================================================================
# Testes do Padrão Singleton
# =============================================================================


def test_garante_instancia_unica_do_singleton(
    mock_usuario_controller,
    mock_autenticacao_controller,
    mock_contrato_controller,
):
    instancia_1 = FacadeSingletonController(
        mock_usuario_controller,
        mock_autenticacao_controller,
        mock_contrato_controller,
    )
    instancia_2 = FacadeSingletonController()

    assert instancia_1 is instancia_2
    assert FacadeSingletonController.obter_instancia() is instancia_1


def test_obter_instancia_sem_inicializacao_previa_lanca_excecao():
    with pytest.raises(RuntimeError, match="ainda não foi instanciada"):
        FacadeSingletonController.obter_instancia()


def test_resetar_instancia_permite_recriar_singleton(
    mock_usuario_controller,
    mock_autenticacao_controller,
    mock_contrato_controller,
):
    instancia_1 = FacadeSingletonController(
        mock_usuario_controller,
        mock_autenticacao_controller,
        mock_contrato_controller,
    )
    FacadeSingletonController.resetar_instancia()

    instancia_2 = FacadeSingletonController(
        mock_usuario_controller,
        mock_autenticacao_controller,
        mock_contrato_controller,
    )
    assert instancia_1 is not instancia_2


# =============================================================================
# Testes de Autenticação na Fachada
# =============================================================================


def test_autenticar_delega_para_autenticacao_controller(
    fachada, mock_autenticacao_controller
):
    usuario_esperado = MagicMock(spec=Usuario)
    mock_autenticacao_controller.autenticar.return_value = usuario_esperado

    resultado = fachada.autenticar("admin", "Senha123!", "GESTOR")

    mock_autenticacao_controller.autenticar.assert_called_once_with(
        identificador="admin", senha="Senha123!", perfil="GESTOR"
    )
    assert resultado is usuario_esperado


# =============================================================================
# Testes de Usuário na Fachada
# =============================================================================


def test_adicionar_usuario_delega_para_usuario_controller(
    fachada, mock_usuario_controller
):
    dados = MagicMock(spec=DadosCadastroUsuario)
    usuario_esperado = MagicMock(spec=Usuario)
    mock_usuario_controller.adicionar.return_value = usuario_esperado

    resultado = fachada.adicionar_usuario(dados)

    mock_usuario_controller.adicionar.assert_called_once_with(dados)
    assert resultado is usuario_esperado


def test_alias_adicionar_compativel_com_usuario_controller(
    fachada, mock_usuario_controller
):
    dados = MagicMock(spec=DadosCadastroUsuario)
    fachada.adicionar(dados)
    mock_usuario_controller.adicionar.assert_called_once_with(dados)


def test_listar_usuarios_delega_para_usuario_controller(
    fachada, mock_usuario_controller
):
    lista_esperada = [MagicMock(spec=Usuario)]
    mock_usuario_controller.listar_todos.return_value = lista_esperada

    resultado = fachada.listar_usuarios()

    mock_usuario_controller.listar_todos.assert_called_once()
    assert resultado == lista_esperada


def test_alias_listar_todos_compativel_com_usuario_controller(
    fachada, mock_usuario_controller
):
    fachada.listar_todos()
    mock_usuario_controller.listar_todos.assert_called_once()


# =============================================================================
# Testes de Contrato na Fachada
# =============================================================================


def test_adicionar_contrato_delega_para_contrato_controller(
    fachada, mock_contrato_controller
):
    dados = MagicMock(spec=DadosCadastroContrato)
    contrato_esperado = MagicMock(spec=Contrato)
    mock_contrato_controller.adicionar.return_value = contrato_esperado

    resultado = fachada.adicionar_contrato(dados, usuario_logado="admin")

    mock_contrato_controller.adicionar.assert_called_once_with(
        dados, usuario_logado="admin"
    )
    assert resultado is contrato_esperado


def test_listar_contratos_delega_para_contrato_controller(
    fachada, mock_contrato_controller
):
    resultado_esperado = ResultadoPaginado([], 1, 1, 0)
    mock_contrato_controller.listar.return_value = resultado_esperado

    resultado = fachada.listar_contratos(
        busca="Tech",
        situacao=SituacaoContrato.ATIVO,
        pagina=2,
        por_pagina=10,
        id_usuario=5,
    )

    mock_contrato_controller.listar.assert_called_once_with(
        busca="Tech",
        situacao=SituacaoContrato.ATIVO,
        pagina=2,
        por_pagina=10,
        id_usuario=5,
    )
    assert resultado is resultado_esperado


def test_alias_listar_compativel_com_contrato_controller(
    fachada, mock_contrato_controller
):
    fachada.listar(busca="teste")
    mock_contrato_controller.listar.assert_called_once_with(
        busca="teste",
        situacao=None,
        pagina=1,
        por_pagina=20,
        id_usuario=None,
    )


def test_buscar_contrato_por_numero_delega(
    fachada, mock_contrato_controller
):
    contrato_esperado = MagicMock(spec=Contrato)
    mock_contrato_controller.buscar_por_numero.return_value = contrato_esperado

    resultado = fachada.buscar_contrato_por_numero("123/2026")
    mock_contrato_controller.buscar_por_numero.assert_called_once_with("123/2026")
    assert resultado is contrato_esperado

    fachada.buscar_por_numero("123/2026")
    assert mock_contrato_controller.buscar_por_numero.call_count == 2


def test_atualizar_contrato_delega(fachada, mock_contrato_controller):
    dados = MagicMock(spec=DadosCadastroContrato)
    fachada.atualizar_contrato(
        "123/2026", dados, nova_situacao=SituacaoContrato.ATIVO, usuario_logado="admin"
    )
    mock_contrato_controller.atualizar.assert_called_once_with(
        numero_atual="123/2026",
        dados=dados,
        nova_situacao=SituacaoContrato.ATIVO,
        usuario_logado="admin",
    )


def test_encerrar_contrato_delega(fachada, mock_contrato_controller):
    fachada.encerrar_contrato("123/2026", usuario_logado="admin")
    mock_contrato_controller.encerrar.assert_called_once_with(
        "123/2026", usuario_logado="admin"
    )


def test_validar_recebimento_evidencia_delega(fachada, mock_contrato_controller):
    fachada.validar_recebimento_evidencia("123/2026")
    mock_contrato_controller.validar_recebimento_evidencia.assert_called_once_with(
        "123/2026"
    )


def test_remover_contrato_delega(fachada, mock_contrato_controller):
    mock_contrato_controller.remover.return_value = True
    removido = fachada.remover_contrato("123/2026", confirmado=True, usuario_logado="admin")

    mock_contrato_controller.remover.assert_called_once_with(
        numero="123/2026", confirmado=True, usuario_logado="admin"
    )
    assert removido is True


def test_vincular_e_desvincular_usuario_delega(fachada, mock_contrato_controller):
    fachada.vincular_usuario_contrato("123/2026", 10, usuario_logado="admin")
    mock_contrato_controller.vincular.assert_called_once_with(
        numero="123/2026", id_usuario=10, usuario_logado="admin"
    )

    fachada.desvincular_usuario_contrato("123/2026", 10, usuario_logado="admin")
    mock_contrato_controller.desvincular.assert_called_once_with(
        numero="123/2026", id_usuario=10, usuario_logado="admin"
    )


# =============================================================================
# Testes do Método de Contagem de Entidades
# =============================================================================


def test_contar_entidades_soma_usuarios_contratos_e_evidencias(
    fachada,
    mock_usuario_controller,
    mock_contrato_controller,
    mock_evidencia_repositorio,
):
    mock_usuario_controller.listar_todos.return_value = [
        MagicMock(spec=Usuario),
        MagicMock(spec=Usuario),
        MagicMock(spec=Usuario),
    ]  # 3 usuários
    mock_contrato_controller.listar.return_value = ResultadoPaginado(
        itens=[],
        pagina_atual=1,
        total_paginas=1,
        total_itens=4,
    )  # 4 contratos
    mock_evidencia_repositorio.listar.return_value = [
        MagicMock(),
        MagicMock(),
    ]  # 2 evidências

    total = fachada.contar_entidades()
    assert total == 3 + 4 + 2  # 9

    assert fachada.quantidade_entidades_cadastradas() == 9

    detalhes = fachada.contar_entidades_detalhado()
    assert detalhes == {
        "usuarios": 3,
        "contratos": 4,
        "evidencias": 2,
        "total": 9,
    }


def test_contar_entidades_sem_evidencia_repositorio_retorna_soma(
    mock_usuario_controller,
    mock_contrato_controller,
):
    mock_usuario_controller.listar_todos.return_value = [MagicMock()]
    mock_contrato_controller.listar.return_value = ResultadoPaginado(
        itens=[],
        pagina_atual=1,
        total_paginas=1,
        total_itens=2,
    )
    fachada = FacadeSingletonController(
        usuario_controller=mock_usuario_controller,
        contrato_controller=mock_contrato_controller,
        evidencia_repositorio=None,
    )

    assert fachada.contar_entidades() == 3
