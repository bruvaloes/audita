"""Vincular e desvincular usuário são alterações do contrato e entram no log
de auditoria (NF004)."""
import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from log.log_auditoria_memoria import LogAuditoriaMemoria
from log.operacao_log import OperacaoLog
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria


@pytest.fixture
def log():
    return LogAuditoriaMemoria()


@pytest.fixture
def funcionario():
    return Usuario(0, "Carlos", "11144477735", "carlos@email.com", "carlos",
                   "hash", Perfil.FUNCIONARIO)


@pytest.fixture
def controller(log, funcionario):
    usuarios = UsuarioRepositorioMemoria()
    usuarios.salvar(funcionario)
    return ContratoController(
        repositorio=ContratoRepositorioMemoria(),
        controle_acesso=ControleAcesso(),
        usuario_repositorio=usuarios,
        log=log,
    )


@pytest.fixture
def contrato(controller, gestor):
    return controller.adicionar(gestor, DadosCadastroContrato(
        numero="CT-1", empresa_contratada="Empresa Alpha Ltda",
        vigencia_inicio="01/01/2026", vigencia_fim="31/12/2026"))


def test_vincular_deve_registrar_no_log(
        controller, contrato, funcionario, gestor, log):
    controller.vincular(gestor, "CT-1", funcionario.id)

    registro = log.listar()[-1]
    assert (registro.operacao, registro.usuario) == (
        OperacaoLog.EDICAO, gestor.login)
    assert "vinculado ao contrato CT-1" in registro.detalhes


def test_desvincular_deve_registrar_no_log(
        controller, contrato, funcionario, gestor, log):
    controller.vincular(gestor, "CT-1", funcionario.id)
    controller.desvincular(gestor, "CT-1", funcionario.id)

    assert "desvinculado do contrato CT-1" in log.listar()[-1].detalhes


def test_vincular_de_novo_o_mesmo_usuario_nao_deve_duplicar_o_registro(
        controller, contrato, funcionario, gestor, log):
    controller.vincular(gestor, "CT-1", funcionario.id)
    controller.vincular(gestor, "CT-1", funcionario.id)

    assert len(log.listar()) == 2  # o cadastro e um único vínculo
