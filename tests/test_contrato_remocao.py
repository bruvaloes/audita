"""Testes de remoção de contrato (RF 07).

Cobre os cenários de aceite C1 a C3 e regras RN07.1 a RN07.3:
- C1: Remoção permitida (sem evidências e confirmada) -> some da listagem
- C2: Remoção cancelada -> contrato permanece na listagem
- C3: Remoção bloqueada (com evidências) -> recusa com "Contrato com evidências não pode ser removido; encerre-o"
- RN07.3: Log de auditoria (EXCLUSAO)
"""
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


@pytest.fixture
def repo_contrato():
    return ContratoRepositorioMemoria()


@pytest.fixture
def repo_evidencia():
    return EvidenciaRepositorioMemoria()


@pytest.fixture
def log():
    return LogAuditoriaMemoria()


@pytest.fixture
def controller(repo_contrato, repo_evidencia, log):
    return ContratoController(
        repositorio=repo_contrato,
        controle_acesso=ControleAcesso(),
        evidencia_repositorio=repo_evidencia,
        relogio=lambda: datetime(2026, 10, 28, 16, 0, 0),
        log=log,
    )


@pytest.fixture
def contrato_cadastrado(controller, gestor):
    return controller.adicionar(gestor,
        DadosCadastroContrato(
            numero="CT-2026-001",
            empresa_contratada="Empresa Limpeza Ltda",
            vigencia_inicio="01/01/2026",
            vigencia_fim="31/12/2026",
        ),
    )


def test_c1_remocao_sem_evidencias_e_confirmada(
    controller, contrato_cadastrado, log, gestor
):
    removido = controller.remover(gestor,
        "CT-2026-001", confirmado=True
    )
    assert removido is True

    # Não deve mais aparecer na listagem
    itens, _ = controller.listar(gestor)
    assert len(itens) == 0

    # RN07.3: Log de auditoria EXCLUSAO
    registros = log.listar()
    # 1 do cadastro + 1 da exclusão
    assert len(registros) == 2
    assert registros[1].operacao == OperacaoLog.EXCLUSAO
    assert "removido" in registros[1].detalhes.lower()


def test_c2_remocao_cancelada_permanece(controller, contrato_cadastrado, gestor):
    removido = controller.remover(gestor, "CT-2026-001", confirmado=False)
    assert removido is False

    # Permanece na listagem
    itens, _ = controller.listar(gestor)
    assert len(itens) == 1
    assert itens[0].numero == "CT-2026-001"


def test_c3_remocao_bloqueada_com_evidencias(
    controller, contrato_cadastrado, repo_evidencia, gestor
):
    # Registra uma evidência vinculada a este contrato
    repo_evidencia.salvar(
        Evidencia(
            id=0,
            caminho_imagem="img.jpg",
            enviada_em=datetime(2026, 10, 28, 12, 0),
            geolocalizacao=None,
            origem=OrigemEvidencia.CAMERA,
            situacao=SituacaoValidacao.PENDENTE,
            id_funcionario=10,
            numero_contrato="CT-2026-001",
            nome_tarefa="Limpeza do Bloco A",
        )
    )

    with pytest.raises(ContratoComEvidenciasError) as exc_info:
        controller.remover(gestor, "CT-2026-001", confirmado=True)

    assert "Contrato com evidências não pode ser removido; encerre-o" in str(
        exc_info.value
    )

    # Confere que o contrato continua intacto no repositório
    itens, _ = controller.listar(gestor)
    assert len(itens) == 1
