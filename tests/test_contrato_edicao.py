"""Testes de edição e encerramento de contrato (RF 06).

Cobre os cenários de aceite C1 a C3 e regras RN06.1 a RN06.3:
- C1: Edição válida -> a listagem mostra o novo valor e log registra a alteração
- C2: Novo número pertence a outro contrato -> "Número de contrato já cadastrado"
- C3: Encerramento -> contrato ENCERRADO não recebe mais evidências (RN06.2)
- RN06.3: Log de auditoria (EDICAO) com valor anterior e novo
"""
from datetime import datetime
import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.situacao_contrato import SituacaoContrato
from excecao.validacao_error import (
    ContratoJaEncerradoError,
    ContratoNumeroJaCadastradoError,
    ValidacaoError,
)
from log.log_auditoria_memoria import LogAuditoriaMemoria
from log.operacao_log import OperacaoLog
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria


@pytest.fixture
def repo():
    return ContratoRepositorioMemoria()


@pytest.fixture
def log():
    return LogAuditoriaMemoria()


@pytest.fixture
def controller(repo, log):
    return ContratoController(
        repositorio=repo,
        controle_acesso=ControleAcesso(),
        relogio=lambda: datetime(2026, 10, 28, 15, 0, 0),
        log=log,
    )


def test_c1_edicao_valida_altera_empresa_e_gera_log(controller, log, gestor):
    controller.adicionar(gestor,
        DadosCadastroContrato(
            numero="CT-2026-001",
            empresa_contratada="Empresa Inicial Ltda",
            vigencia_inicio="01/01/2026",
            vigencia_fim="31/12/2026",
        ),
    )

    dados_atualizacao = DadosCadastroContrato(
        numero="CT-2026-001",
        empresa_contratada="Empresa Atualizada S/A",
        vigencia_inicio="01/01/2026",
        vigencia_fim="31/12/2026",
    )

    atualizado = controller.atualizar(gestor,
        "CT-2026-001", dados_atualizacao
    )

    assert atualizado.empresa_contratada == "Empresa Atualizada S/A"

    # Confere na listagem
    contratos, _ = controller.listar(gestor)
    assert contratos[0].empresa_contratada == "Empresa Atualizada S/A"

    # RN06.3: Log de auditoria com anterior e novo
    registros = log.listar()
    assert len(registros) == 2  # 1 do cadastro + 1 da edição
    reg_edicao = registros[1]
    assert reg_edicao.operacao == OperacaoLog.EDICAO
    assert "anterior=" in reg_edicao.detalhes
    assert "Empresa Inicial Ltda" in reg_edicao.detalhes
    assert "novo=" in reg_edicao.detalhes
    assert "Empresa Atualizada S/A" in reg_edicao.detalhes


def test_c2_numero_de_outro_contrato_rejeitado(controller, gestor):
    controller.adicionar(gestor,
        DadosCadastroContrato(
            numero="CT-2026-001",
            empresa_contratada="Empresa Alpha",
            vigencia_inicio="01/01/2026",
            vigencia_fim="31/12/2026",
        )
    )
    controller.adicionar(gestor,
        DadosCadastroContrato(
            numero="CT-2026-002",
            empresa_contratada="Empresa Beta",
            vigencia_inicio="01/01/2026",
            vigencia_fim="31/12/2026",
        )
    )

    # Tenta mudar o número do CT-001 para o do CT-002
    dados_conflito = DadosCadastroContrato(
        numero="CT-2026-002",
        empresa_contratada="Empresa Alpha",
        vigencia_inicio="01/01/2026",
        vigencia_fim="31/12/2026",
    )

    with pytest.raises(ContratoNumeroJaCadastradoError) as exc_info:
        controller.atualizar(gestor, "CT-2026-001", dados_conflito)

    assert "Número de contrato já cadastrado" in str(exc_info.value)


def test_c3_encerramento_impede_novas_evidencias(controller, gestor):
    contrato = controller.adicionar(gestor,
        DadosCadastroContrato(
            numero="CT-2026-001",
            empresa_contratada="Empresa Alpha",
            vigencia_inicio="01/01/2026",
            vigencia_fim="31/12/2026",
        )
    )
    assert contrato.situacao == SituacaoContrato.ATIVO

    # Encerrando o contrato
    encerrado = controller.encerrar(gestor, "CT-2026-001")
    assert encerrado.situacao == SituacaoContrato.ENCERRADO

    # RN06.2: Validação de recebimento de evidência bloqueia
    with pytest.raises(ValidacaoError) as exc_info:
        controller.validar_recebimento_evidencia("CT-2026-001")

    assert "encerrado" in str(exc_info.value).lower()


def test_encerrar_contrato_ja_encerrado_deve_ser_recusado_sem_novo_registro_no_log(
        controller, gestor, log):
    controller.adicionar(gestor, DadosCadastroContrato(
        numero="CT-1", empresa_contratada="Empresa Alpha",
        vigencia_inicio="01/01/2026", vigencia_fim="31/12/2026"))
    controller.encerrar(gestor, "CT-1")
    registros_antes = len(log.listar())

    with pytest.raises(ContratoJaEncerradoError) as erro:
        controller.encerrar(gestor, "CT-1")

    assert str(erro.value) == "Contrato já está encerrado"
    assert len(log.listar()) == registros_antes
