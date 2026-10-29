"""Testes de cadastro de contrato (RF 04).

Cobre os cenários de aceite C1 a C5 e auditoria RN04.5:
- C1: Cadastro válido (criado ATIVO e aparece na listagem)
- C2: Número duplicado ("Número de contrato já cadastrado")
- C3: Vigência inválida ("A data de fim deve ser igual ou posterior à data de início")
- C4: Arquivo inválido (.exe ou > 30 MB)
- C5: Empresa vazia (indica campo obrigatório)
- RN04.5: Registro no log de auditoria (operação CADASTRO)
"""
from datetime import datetime
import pytest

from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.situacao_contrato import SituacaoContrato
from excecao.validacao_error import (
    ArquivoInvalidoError,
    CampoObrigatorioError,
    ContratoNumeroJaCadastradoError,
    VigenciaInvalidaError,
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
        relogio=lambda: datetime(2026, 10, 28, 14, 0, 0),
        log=log,
    )


@pytest.fixture
def dados_validos():
    return DadosCadastroContrato(
        numero="CT-2026-001",
        empresa_contratada="Empresa Alpha Ltda",
        vigencia_inicio="01/01/2026",
        vigencia_fim="31/12/2026",
        arquivo="minuta.pdf",
    )


def test_c1_cadastro_valido(controller, repo, log, dados_validos):
    contrato = controller.adicionar(dados_validos, usuario_logado="gestor1")

    assert contrato.id > 0
    assert contrato.numero == "CT-2026-001"
    assert contrato.empresa_contratada == "Empresa Alpha Ltda"
    assert contrato.situacao == SituacaoContrato.ATIVO

    # Aparece na listagem
    itens, total_paginas = controller.listar()
    assert len(itens) == 1
    assert itens[0].numero == "CT-2026-001"

    # RN04.5: Gera log de auditoria CADASTRO
    registros = log.listar()
    assert len(registros) == 1
    assert registros[0].operacao == OperacaoLog.CADASTRO
    assert registros[0].usuario == "gestor1"
    assert "CT-2026-001" in registros[0].detalhes


def test_c2_numero_duplicado(controller, dados_validos):
    controller.adicionar(dados_validos)

    dados_duplicado = DadosCadastroContrato(
        numero="CT-2026-001",
        empresa_contratada="Outra Empresa Ltda",
        vigencia_inicio="01/02/2026",
        vigencia_fim="31/12/2026",
    )

    with pytest.raises(ContratoNumeroJaCadastradoError) as exc_info:
        controller.adicionar(dados_duplicado)

    assert "Número de contrato já cadastrado" in str(exc_info.value)


def test_c3_vigencia_invalida_fim_anterior_ao_inicio(controller, dados_validos):
    dados_validos.vigencia_inicio = "31/12/2026"
    dados_validos.vigencia_fim = "01/01/2026"

    with pytest.raises(VigenciaInvalidaError) as exc_info:
        controller.adicionar(dados_validos)

    assert "A data de fim deve ser igual ou posterior à data de início" in str(exc_info.value)


def test_c4_arquivo_invalido_extensao_exe(controller, dados_validos):
    dados_validos.arquivo = "programa.exe"

    with pytest.raises(ArquivoInvalidoError) as exc_info:
        controller.adicionar(dados_validos)

    msg = str(exc_info.value).lower()
    assert "pdf" in msg or "docx" in msg or "30 mb" in msg


def test_c4_arquivo_invalido_tamanho_acima_de_30mb(controller, dados_validos, tmp_path):
    arquivo_gigante = tmp_path / "contrato.pdf"
    # Cria arquivo esparso simulando > 30 MB
    with open(arquivo_gigante, "wb") as f:
        f.seek(31 * 1024 * 1024)
        f.write(b"0")

    dados_validos.arquivo = str(arquivo_gigante)

    with pytest.raises(ArquivoInvalidoError) as exc_info:
        controller.adicionar(dados_validos)

    assert "30 mb" in str(exc_info.value).lower()


def test_c5_empresa_contratada_vazia(controller, dados_validos):
    dados_validos.empresa_contratada = "   "

    with pytest.raises(CampoObrigatorioError) as exc_info:
        controller.adicionar(dados_validos)

    assert "Empresa contratada" in str(exc_info.value)
