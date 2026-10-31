"""Renumerar um contrato não pode deixar evidências sem contrato: as
evidências apontam para o número (RF 06)."""
from datetime import datetime

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.evidencia import Evidencia
from entidade.origem_evidencia import OrigemEvidencia
from entidade.situacao_validacao import SituacaoValidacao
from excecao.validacao_error import ContratoComEvidenciasError
from log.log_auditoria_memoria import LogAuditoriaMemoria
from log.operacao_log import OperacaoLog
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria


def dados(numero="CT-1"):
    return DadosCadastroContrato(
        numero=numero, empresa_contratada="Empresa Alpha Ltda",
        vigencia_inicio="01/01/2026", vigencia_fim="31/12/2026")


@pytest.fixture
def evidencias():
    return EvidenciaRepositorioMemoria()


@pytest.fixture
def log():
    return LogAuditoriaMemoria()


@pytest.fixture
def controller(evidencias, log):
    return ContratoController(
        repositorio=ContratoRepositorioMemoria(),
        controle_acesso=ControleAcesso(),
        evidencia_repositorio=evidencias,
        relogio=lambda: datetime(2026, 10, 28, 9, 0, 0),
        log=log,
    )


def _evidencia(numero_contrato):
    return Evidencia(
        0, "foto.jpg", datetime(2026, 10, 28), None, OrigemEvidencia.CAMERA,
        SituacaoValidacao.PENDENTE, 1, numero_contrato, "Limpeza")


def test_numero_nao_pode_mudar_quando_ha_evidencias(
        controller, gestor, evidencias):
    controller.adicionar(gestor, dados("CT-1"))
    evidencias.salvar(_evidencia("CT-1"))

    with pytest.raises(ContratoComEvidenciasError):
        controller.atualizar(gestor, "CT-1", dados("CT-2"))

    assert controller.buscar_por_numero(gestor, "CT-1") is not None
    assert controller.buscar_por_numero(gestor, "CT-2") is None


def test_numero_pode_mudar_sem_evidencias_e_mantem_os_vinculos(
        controller, gestor, log):
    contrato = controller.adicionar(gestor, dados("CT-1"))
    contrato.usuarios_vinculados.append(7)

    renomeado = controller.atualizar(gestor, "CT-1", dados("CT-2"))

    assert renomeado.numero == "CT-2"
    assert renomeado.usuarios_vinculados == [7]
    assert controller.buscar_por_numero(gestor, "CT-1") is None
    assert log.listar()[-1].operacao == OperacaoLog.EDICAO
