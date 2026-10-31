from datetime import datetime
from unittest.mock import MagicMock
import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController, ResultadoPaginado
from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.facade_singleton_controller import FacadeSingletonController
from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
from controle.sessao import Sessao
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import ValidadorCadastroUsuario
from entidade.contrato import Contrato
from entidade.evidencia import Evidencia
from entidade.origem_evidencia import OrigemEvidencia
from entidade.situacao_contrato import SituacaoContrato
from entidade.situacao_validacao import SituacaoValidacao
from entidade.usuario import Usuario
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.contrato_fronteira import ContratoFronteira
from fronteira.painel_fronteira import PainelFronteira
from fronteira.usuario_fronteira import UsuarioFronteira
from persistencia.acesso_repositorio_memoria import AcessoRepositorioMemoria
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.evidencia_repositorio import EvidenciaRepositorio
from persistencia.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria


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
    solicitante = MagicMock(spec=Usuario)

    resultado = fachada.listar_usuarios(solicitante)

    mock_usuario_controller.listar_todos.assert_called_once_with(solicitante)
    assert resultado == lista_esperada


def test_alias_listar_todos_compativel_com_usuario_controller(
    fachada, mock_usuario_controller
):
    solicitante = MagicMock(spec=Usuario)
    fachada.listar_todos(solicitante)
    mock_usuario_controller.listar_todos.assert_called_once_with(solicitante)


# =============================================================================
# Testes de Contrato na Fachada
# =============================================================================


def test_adicionar_contrato_delega_para_contrato_controller(
    fachada, mock_contrato_controller
):
    dados = MagicMock(spec=DadosCadastroContrato)
    contrato_esperado = MagicMock(spec=Contrato)
    mock_contrato_controller.adicionar.return_value = contrato_esperado
    solicitante = MagicMock(spec=Usuario)

    resultado = fachada.adicionar_contrato(solicitante, dados)

    mock_contrato_controller.adicionar.assert_called_once_with(solicitante, dados)
    assert resultado is contrato_esperado


def test_listar_contratos_delega_para_contrato_controller(
    fachada, mock_contrato_controller
):
    resultado_esperado = ResultadoPaginado([], 1, 1, 0)
    mock_contrato_controller.listar.return_value = resultado_esperado
    solicitante = MagicMock(spec=Usuario)

    resultado = fachada.listar_contratos(
        solicitante,
        busca="Tech",
        situacao=SituacaoContrato.ATIVO,
        pagina=2,
        por_pagina=10,
        id_usuario=5,
    )

    mock_contrato_controller.listar.assert_called_once_with(
        solicitante,
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
    solicitante = MagicMock(spec=Usuario)
    fachada.listar(solicitante, busca="teste")
    mock_contrato_controller.listar.assert_called_once_with(
        solicitante,
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
    solicitante = MagicMock(spec=Usuario)

    resultado = fachada.buscar_contrato_por_numero(solicitante, "123/2026")
    mock_contrato_controller.buscar_por_numero.assert_called_once_with(solicitante, "123/2026")
    assert resultado is contrato_esperado

    fachada.buscar_por_numero(solicitante, "123/2026")
    assert mock_contrato_controller.buscar_por_numero.call_count == 2


def test_atualizar_contrato_delega(fachada, mock_contrato_controller):
    dados = MagicMock(spec=DadosCadastroContrato)
    solicitante = MagicMock(spec=Usuario)
    fachada.atualizar_contrato(
        solicitante, "123/2026", dados, nova_situacao=SituacaoContrato.ATIVO
    )
    mock_contrato_controller.atualizar.assert_called_once_with(
        solicitante,
        numero_atual="123/2026",
        dados=dados,
        nova_situacao=SituacaoContrato.ATIVO,
    )


def test_encerrar_contrato_delega(fachada, mock_contrato_controller):
    solicitante = MagicMock(spec=Usuario)
    fachada.encerrar_contrato(solicitante, "123/2026")
    mock_contrato_controller.encerrar.assert_called_once_with(
        solicitante, "123/2026"
    )


def test_validar_recebimento_evidencia_delega(fachada, mock_contrato_controller):
    fachada.validar_recebimento_evidencia("123/2026")
    mock_contrato_controller.validar_recebimento_evidencia.assert_called_once_with(
        "123/2026"
    )


def test_remover_contrato_delega(fachada, mock_contrato_controller):
    mock_contrato_controller.remover.return_value = True
    solicitante = MagicMock(spec=Usuario)
    removido = fachada.remover_contrato(solicitante, "123/2026", confirmado=True)

    mock_contrato_controller.remover.assert_called_once_with(
        solicitante=solicitante, numero="123/2026", confirmado=True
    )
    assert removido is True


def test_vincular_e_desvincular_usuario_delega(fachada, mock_contrato_controller):
    solicitante = MagicMock(spec=Usuario)
    fachada.vincular_usuario_contrato(solicitante, "123/2026", 10)
    mock_contrato_controller.vincular.assert_called_once_with(
        solicitante=solicitante, numero="123/2026", id_usuario=10
    )

    fachada.desvincular_usuario_contrato(solicitante, "123/2026", 10)
    mock_contrato_controller.desvincular.assert_called_once_with(
        solicitante=solicitante, numero="123/2026", id_usuario=10
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
    mock_usuario_controller.contar.return_value = 3
    mock_contrato_controller.contar.return_value = 4
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
    mock_usuario_controller.contar.return_value = 1
    mock_contrato_controller.contar.return_value = 2
    fachada = FacadeSingletonController(
        usuario_controller=mock_usuario_controller,
        contrato_controller=mock_contrato_controller,
        evidencia_repositorio=None,
    )

    assert fachada.contar_entidades() == 3


# =============================================================================
# Testes de Integração com as Fronteiras (Issue #19 - Etapa 2)
# =============================================================================


def test_fronteiras_recebem_apenas_facade_singleton_controller(fachada):
    """Verifica que as fronteiras aceitam FacadeSingletonController como controller único."""
    sessao = Sessao()
    controle_acesso = ControleAcesso()

    contrato_fronteira = ContratoFronteira(fachada, sessao)
    painel_fronteira = PainelFronteira(sessao, controle_acesso)
    autenticacao_fronteira = AutenticacaoFronteira(fachada, painel_fronteira)
    usuario_fronteira = UsuarioFronteira(fachada, autenticacao_fronteira, sessao)

    assert contrato_fronteira._controller is fachada
    assert autenticacao_fronteira._controller is fachada
    assert usuario_fronteira._controller is fachada


def test_fluxo_integracao_completo_via_fachada():
    """Fluxo de ponta a ponta com repositórios em memória via fachada."""
    usuario_repo = UsuarioRepositorioMemoria()
    acesso_repo = AcessoRepositorioMemoria()
    contrato_repo = ContratoRepositorioMemoria()
    evidencia_repo = EvidenciaRepositorioMemoria()

    hash_senha = HashSenhaArgon2()
    controle_acesso = ControleAcesso()
    validador_usuario = ValidadorCadastroUsuario(usuario_repo)
    controller_usuario = UsuarioController(
        usuario_repo, validador_usuario, hash_senha, controle_acesso
    )
    autenticacao = AutenticacaoController(usuario_repo, acesso_repo, hash_senha)
    contrato_controller = ContratoController(
        repositorio=contrato_repo,
        controle_acesso=controle_acesso,
        evidencia_repositorio=evidencia_repo,
        usuario_repositorio=usuario_repo,
    )

    fachada = FacadeSingletonController(
        usuario_controller=controller_usuario,
        autenticacao_controller=autenticacao,
        contrato_controller=contrato_controller,
        evidencia_repositorio=evidencia_repo,
    )

    # 1. Contagem inicial vazia
    assert fachada.contar_entidades() == 0

    # 2. Cadastro de usuário via fachada
    dados_usuario = DadosCadastroUsuario(
        nome="Gestor do Sistema",
        cpf="11144477735",
        email="gestor@audita.gov.br",
        login="gestor",
        senha="Gestor@123456",
        confirmacao_senha="Gestor@123456",
        perfil="GESTOR",
        aceite_termos="s",
    )
    usuario_criado = fachada.adicionar_usuario(dados_usuario)
    assert usuario_criado.id > 0
    assert fachada.contar_entidades() == 1

    # 3. Autenticação via fachada
    usuario_autenticado = fachada.autenticar(
        identificador="gestor",
        senha="Gestor@123456",
        perfil="GESTOR",
    )
    assert usuario_autenticado.id == usuario_criado.id

    # 4. Cadastro e listagem de contrato via fachada
    dados_contrato = DadosCadastroContrato(
        numero="001/2026",
        empresa_contratada="Empresa Alpha Ltda",
        vigencia_inicio="01/01/2026",
        vigencia_fim="31/12/2026",
    )
    contrato_criado = fachada.adicionar_contrato(usuario_autenticado, dados_contrato)
    assert contrato_criado.numero == "001/2026"
    assert fachada.contar_entidades() == 2

    # 5. Adição de evidência no repositório e contagem total
    evidencia = Evidencia(
        id=0,
        caminho_imagem="comprovante.jpg",
        enviada_em=datetime.now(),
        geolocalizacao=None,
        origem=OrigemEvidencia.CAMERA,
        situacao=SituacaoValidacao.PENDENTE,
        id_funcionario=usuario_criado.id,
        numero_contrato="001/2026",
        nome_tarefa="Limpeza de vidros",
    )
    evidencia_repo.salvar(evidencia)

    # Agora deve somar 1 usuário + 1 contrato + 1 evidência = 3
    assert fachada.contar_entidades() == 3
    detalhes = fachada.contar_entidades_detalhado()
    assert detalhes == {
        "usuarios": 1,
        "contratos": 1,
        "evidencias": 1,
        "total": 3,
    }
