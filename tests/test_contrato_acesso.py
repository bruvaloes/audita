"""RF 03 nas operações de contrato: o controller confere o perfil, e não só o
menu; e a renumeração não deixa evidências sem contrato."""
from datetime import datetime

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.acesso_negado_error import AcessoNegadoError
from excecao.validacao_error import ContratoComEvidenciasError
from log.log_auditoria_memoria import LogAuditoriaMemoria
from log.operacao_log import OperacaoLog
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from entidade.evidencia import Evidencia
from entidade.origem_evidencia import OrigemEvidencia
from entidade.situacao_validacao import SituacaoValidacao


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
        usuario_repositorio=UsuarioRepositorioMemoria(),
        relogio=lambda: datetime(2026, 10, 28, 9, 0, 0),
        log=log,
    )


def usuario(perfil):
    return Usuario(5, "Ana", "52998224725", "ana@email.com", "ana", "hash",
                   perfil)


OPERACOES = {
    "adicionar": lambda c, u: c.adicionar(u, dados("CT-9")),
    "listar": lambda c, u: c.listar(u),
    "buscar_por_numero": lambda c, u: c.buscar_por_numero(u, "CT-1"),
    "atualizar": lambda c, u: c.atualizar(u, "CT-1", dados()),
    "encerrar": lambda c, u: c.encerrar(u, "CT-1"),
    "remover": lambda c, u: c.remover(u, "CT-1", confirmado=True),
    "vincular": lambda c, u: c.vincular(u, "CT-1", 1),
    "desvincular": lambda c, u: c.desvincular(u, "CT-1", 1),
}


@pytest.mark.parametrize("operacao", OPERACOES)
@pytest.mark.parametrize("perfil", [None, Perfil.FISCAL, Perfil.FUNCIONARIO])
def test_perfil_sem_permissao_nao_deve_operar_contratos(
        controller, gestor, operacao, perfil):
    controller.adicionar(gestor, dados())
    solicitante = usuario(perfil) if perfil else None

    with pytest.raises(AcessoNegadoError):
        OPERACOES[operacao](controller, solicitante)


def test_acesso_negado_nao_deve_alterar_nada_nem_gerar_log(
        controller, gestor, log):
    controller.adicionar(gestor, dados())
    registros_antes = len(log.listar())

    with pytest.raises(AcessoNegadoError):
        controller.remover(usuario(Perfil.FISCAL), "CT-1", confirmado=True)

    assert controller.buscar_por_numero(gestor, "CT-1") is not None
    assert len(log.listar()) == registros_antes


def test_log_deve_registrar_o_login_de_quem_cadastrou(
        controller, gestor, log):
    controller.adicionar(gestor, dados())

    assert log.listar()[-1].usuario == gestor.login


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
    assert log.listar()[-1].operacao == \
        OperacaoLog.EDICAO


# --- Fronteira: o painel só oferece contratos a quem tem permissão ----------

def _painel_com_contratos(controller, sessao):
    from controle.acesso.operacao import Operacao
    from fronteira.contrato_fronteira import ContratoFronteira
    from fronteira.painel_fronteira import AcaoDoPainel, PainelFronteira

    fronteira = ContratoFronteira(controller, sessao)
    painel = PainelFronteira(sessao, ControleAcesso())
    painel.registrar(AcaoDoPainel(
        Operacao.CADASTRAR_CONTRATO, "Cadastrar contrato",
        fronteira.cadastrar_contrato))
    return painel


def test_painel_do_gestor_deve_cadastrar_contrato(
        controller, sessao, gestor, monkeypatch, capsys):
    respostas = iter(["1", "CT-7", "Empresa Beta", "01/01/2026",
                      "31/12/2026", "", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    _painel_com_contratos(controller, sessao).abrir(gestor)

    assert "1 - Cadastrar contrato" in capsys.readouterr().out
    assert controller.buscar_por_numero(gestor, "CT-7") is not None


def test_painel_do_funcionario_nao_deve_oferecer_contratos(
        controller, sessao, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "0")

    _painel_com_contratos(controller, sessao).abrir(usuario(Perfil.FUNCIONARIO))

    assert "Cadastrar contrato" not in capsys.readouterr().out
