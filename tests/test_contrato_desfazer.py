"""Testes de desfazer a última atualização de contrato (Memento, Issue #26).

Cobre os critérios de aceite C1 a C11:
- C1: desfazer edição -> valores voltam
- C2: desfazer encerramento -> situação volta a ATIVO
- C3: desfazer vincular e desvincular usuário
- C4: desfazer renumeração -> número antigo volta, novo deixa de existir
- C5: só a última atualização é desfeita
- C6: nova atualização substitui a anterior no histórico
- C7: remover contrato limpa o histórico
- C8: perfil sem permissão não desfaz
- C9: funciona em memória e SQLite
- C10: desfazer gera registro EDICAO no log
- C11: desfazer não cria um novo ponto de desfazer
"""
from datetime import datetime

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.perfil import Perfil
from entidade.situacao_contrato import SituacaoContrato
from entidade.usuario import Usuario
from excecao.acesso_negado_error import AcessoNegadoError
from excecao.persistencia_error import EscritaPersistenciaError
from excecao.validacao_error import NadaParaDesfazerError
from infraestrutura.contrato_repositorio_memoria import ContratoRepositorioMemoria
from infraestrutura.contrato_repositorio_sqlite import ContratoRepositorioSQLite
from infraestrutura.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from log.log_auditoria_memoria import LogAuditoriaMemoria
from log.operacao_log import OperacaoLog
from negocio.contrato_repositorio import ContratoRepositorio


def dados(numero="CT-2026-001", empresa="Empresa Alpha Ltda"):
    return DadosCadastroContrato(
        numero=numero, empresa_contratada=empresa,
        vigencia_inicio="01/01/2026", vigencia_fim="31/12/2026")


@pytest.fixture
def repo():
    return ContratoRepositorioMemoria()


@pytest.fixture
def repo_usuario():
    return UsuarioRepositorioMemoria()


@pytest.fixture
def log():
    return LogAuditoriaMemoria()


@pytest.fixture
def controller(repo, repo_usuario, log):
    return ContratoController(
        repositorio=repo,
        controle_acesso=ControleAcesso(),
        usuario_repositorio=repo_usuario,
        relogio=lambda: datetime(2026, 11, 25, 10, 0, 0),
        log=log,
    )


def funcionario(repo_usuario):
    return repo_usuario.salvar(
        Usuario(
            id=0, nome="Carlos Funcionario", cpf="11122233344",
            email="carlos@email.com", login="carlos", senha_hash="hash",
            perfil=Perfil.FUNCIONARIO, ativo=True,
        )
    )


def test_c1_deve_desfazer_a_ultima_edicao(controller, log, gestor):
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(empresa="Empresa Nova S/A"))

    restaurado = controller.desfazer_ultima_atualizacao(gestor)

    assert restaurado.empresa_contratada == "Empresa Alpha Ltda"
    assert controller.buscar_por_numero(
        gestor, "CT-2026-001").empresa_contratada == "Empresa Alpha Ltda"


def test_c10_desfazer_gera_registro_edicao_no_log(controller, log, gestor):
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(empresa="Empresa Nova S/A"))

    controller.desfazer_ultima_atualizacao(gestor)

    assert log.listar()[-1].operacao == OperacaoLog.EDICAO


def test_c2_deve_desfazer_o_encerramento(controller, gestor):
    controller.adicionar(gestor, dados())
    controller.encerrar(gestor, "CT-2026-001")

    restaurado = controller.desfazer_ultima_atualizacao(gestor)

    assert restaurado.situacao == SituacaoContrato.ATIVO


def test_c3_deve_desfazer_o_vinculo(controller, repo_usuario, gestor):
    controller.adicionar(gestor, dados())
    usuario = funcionario(repo_usuario)
    controller.vincular(gestor, "CT-2026-001", usuario.id)

    restaurado = controller.desfazer_ultima_atualizacao(gestor)

    assert usuario.id not in restaurado.usuarios_vinculados


def test_c3_deve_desfazer_o_desvinculo(controller, repo_usuario, gestor):
    controller.adicionar(gestor, dados())
    usuario = funcionario(repo_usuario)
    controller.vincular(gestor, "CT-2026-001", usuario.id)
    controller.desvincular(gestor, "CT-2026-001", usuario.id)

    restaurado = controller.desfazer_ultima_atualizacao(gestor)

    assert usuario.id in restaurado.usuarios_vinculados


def test_c4_deve_desfazer_a_renumeracao(controller, gestor):
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(numero="CT-2026-002"))

    restaurado = controller.desfazer_ultima_atualizacao(gestor)

    assert restaurado.numero == "CT-2026-001"
    assert controller.buscar_por_numero(gestor, "CT-2026-002") is None
    assert controller.buscar_por_numero(gestor, "CT-2026-001") is not None


def test_c5_segundo_desfazer_deve_informar_que_nao_ha_o_que_desfazer(
        controller, gestor):
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(empresa="Empresa Nova S/A"))
    controller.desfazer_ultima_atualizacao(gestor)

    with pytest.raises(NadaParaDesfazerError):
        controller.desfazer_ultima_atualizacao(gestor)


def test_c5_sem_nenhuma_atualizacao_nao_ha_o_que_desfazer(controller, gestor):
    controller.adicionar(gestor, dados())

    with pytest.raises(NadaParaDesfazerError):
        controller.desfazer_ultima_atualizacao(gestor)


def test_c6_nova_atualizacao_deve_substituir_o_ponto_de_desfazer(
        controller, gestor):
    controller.adicionar(gestor, dados("CT-2026-001", "Empresa Alpha"))
    controller.adicionar(gestor, dados("CT-2026-002", "Empresa Beta"))
    controller.atualizar(
        gestor, "CT-2026-001", dados("CT-2026-001", "Empresa Alpha Nova"))
    controller.atualizar(
        gestor, "CT-2026-002", dados("CT-2026-002", "Empresa Beta Nova"))

    restaurado = controller.desfazer_ultima_atualizacao(gestor)

    assert restaurado.numero == "CT-2026-002"
    assert restaurado.empresa_contratada == "Empresa Beta"
    assert controller.buscar_por_numero(
        gestor, "CT-2026-001").empresa_contratada == "Empresa Alpha Nova"


def test_c7_remover_contrato_deve_limpar_o_historico(controller, gestor):
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(empresa="Empresa Nova S/A"))
    controller.remover(gestor, "CT-2026-001", confirmado=True)

    with pytest.raises(NadaParaDesfazerError):
        controller.desfazer_ultima_atualizacao(gestor)


@pytest.mark.parametrize("perfil", [None, Perfil.FISCAL, Perfil.FUNCIONARIO])
def test_c8_perfil_sem_permissao_nao_deve_desfazer(controller, gestor, perfil):
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(empresa="Empresa Nova S/A"))
    solicitante = Usuario(5, "Ana", "52998224725", "ana@email.com", "ana",
                           "hash", perfil) if perfil else None

    with pytest.raises(AcessoNegadoError):
        controller.desfazer_ultima_atualizacao(solicitante)

    assert controller.buscar_por_numero(
        gestor, "CT-2026-001").empresa_contratada == "Empresa Nova S/A"


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio_implementacao(request, tmp_path) -> ContratoRepositorio:
    if request.param == "memoria":
        return ContratoRepositorioMemoria()
    return ContratoRepositorioSQLite(str(tmp_path / "contrato.db"))


def test_c9_funciona_em_memoria_e_sqlite(repositorio_implementacao, gestor):
    controller = ContratoController(
        repositorio=repositorio_implementacao, controle_acesso=ControleAcesso())
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(numero="CT-2026-002"))

    restaurado = controller.desfazer_ultima_atualizacao(gestor)

    assert restaurado.numero == "CT-2026-001"
    assert controller.buscar_por_numero(gestor, "CT-2026-002") is None


def test_desfazer_renumeracao_que_falha_ao_gravar_nao_deve_perder_o_contrato(
        repositorio_implementacao, gestor):
    controller = ContratoController(
        repositorio=repositorio_implementacao, controle_acesso=ControleAcesso())
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(numero="CT-2026-002"))
    controller.adicionar(gestor, dados("CT-2026-001", "Outra Empresa"))

    with pytest.raises(EscritaPersistenciaError):
        controller.desfazer_ultima_atualizacao(gestor)

    renumerado = controller.buscar_por_numero(gestor, "CT-2026-002")
    assert renumerado is not None
    assert renumerado.empresa_contratada == "Empresa Alpha Ltda"


def test_c11_desfazer_nao_deve_criar_um_novo_ponto_de_desfazer(controller, gestor):
    controller.adicionar(gestor, dados())
    controller.atualizar(gestor, "CT-2026-001", dados(empresa="Empresa Nova S/A"))

    controller.desfazer_ultima_atualizacao(gestor)

    with pytest.raises(NadaParaDesfazerError):
        controller.desfazer_ultima_atualizacao(gestor)


def test_snapshot_nao_deve_mudar_quando_o_contrato_muda(controller, gestor):
    contrato = controller.adicionar(gestor, dados())
    memento = contrato.criar_memento()

    contrato.usuarios_vinculados.append(99)
    contrato.empresa_contratada = "Outra Empresa"

    assert memento.usuarios_vinculados == ()
    assert memento.empresa_contratada == "Empresa Alpha Ltda"
