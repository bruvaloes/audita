"""Testes de vínculo e desvínculo de usuários a contratos (RF 08).

Cobre os cenários de aceite C1 a C3 e regras RN08.1 a RN08.4:
- C1: Vínculo válido (contrato ATIVO e funcionário ATIVO) -> contrato passa a aparecer para o funcionário
- C2: Perfil incompatível (GESTOR) -> recusa com "Perfil não pode ser vinculado a contrato"
- C3: Último fiscal em contrato ATIVO -> recusa com "O contrato deve ter ao menos um fiscal"
- RN08.3: Usuário pode ser vinculado a múltiplos contratos
"""
from datetime import datetime
import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.perfil import Perfil
from entidade.situacao_contrato import SituacaoContrato
from entidade.usuario import Usuario
from excecao.validacao_error import (
    PerfilNaoVinculavelError,
    UltimoFiscalError,
    ValidacaoError,
)
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria


@pytest.fixture
def repo_contrato():
    return ContratoRepositorioMemoria()


@pytest.fixture
def repo_usuario():
    return UsuarioRepositorioMemoria()


@pytest.fixture
def controller(repo_contrato, repo_usuario):
    return ContratoController(
        repositorio=repo_contrato,
        controle_acesso=ControleAcesso(),
        usuario_repositorio=repo_usuario,
    )


@pytest.fixture
def contrato(controller, gestor):
    return controller.adicionar(gestor,
        DadosCadastroContrato(
            numero="CT-2026-001",
            empresa_contratada="Empresa Alpha Ltda",
            vigencia_inicio="01/01/2026",
            vigencia_fim="31/12/2026",
        )
    )


@pytest.fixture
def funcionario_ativo(repo_usuario):
    return repo_usuario.salvar(
        Usuario(
            id=0,
            nome="Carlos Funcionario",
            cpf="11122233344",
            email="carlos@email.com",
            login="carlos",
            senha_hash="hash",
            perfil=Perfil.FUNCIONARIO,
            ativo=True,
        )
    )


@pytest.fixture
def fiscal_ativo(repo_usuario):
    return repo_usuario.salvar(
        Usuario(
            id=0,
            nome="Fernando Fiscal",
            cpf="55566677788",
            email="fernando@email.com",
            login="fernando",
            senha_hash="hash",
            perfil=Perfil.FISCAL,
            ativo=True,
        )
    )


@pytest.fixture
def gestor_ativo(repo_usuario):
    return repo_usuario.salvar(
        Usuario(
            id=0,
            nome="Geraldo Gestor",
            cpf="99988877766",
            email="geraldo@email.com",
            login="geraldo",
            senha_hash="hash",
            perfil=Perfil.GESTOR,
            ativo=True,
        )
    )


def test_c1_vinculo_valido_contrato_aparece_para_funcionario(
    controller, contrato, funcionario_ativo, gestor
):
    # Antes do vínculo, o funcionário não vê o contrato
    resultado_antes = controller.listar(gestor, id_usuario=funcionario_ativo.id)
    assert len(resultado_antes.itens) == 0

    # Vincula o funcionário ao contrato
    controller.vincular(gestor, contrato.numero, funcionario_ativo.id)

    # RN08.4: Agora o contrato aparece para ele
    resultado_depois = controller.listar(gestor, id_usuario=funcionario_ativo.id)
    assert len(resultado_depois.itens) == 1
    assert resultado_depois.itens[0].numero == contrato.numero


def test_c2_perfil_gestor_rejeitado(controller, contrato, gestor_ativo, gestor):
    with pytest.raises(PerfilNaoVinculavelError) as exc_info:
        controller.vincular(gestor, contrato.numero, gestor_ativo.id)

    assert "Perfil não pode ser vinculado a contrato" in str(exc_info.value)


def test_c3_desvincular_ultimo_fiscal_rejeitado(
    controller, contrato, fiscal_ativo, gestor
):
    # Vincula o fiscal ao contrato ATIVO
    controller.vincular(gestor, contrato.numero, fiscal_ativo.id)

    # Tenta desvincular o único fiscal
    with pytest.raises(UltimoFiscalError) as exc_info:
        controller.desvincular(gestor, contrato.numero, fiscal_ativo.id)

    assert "O contrato deve ter ao menos um fiscal" in str(exc_info.value)


def test_desvincular_fiscal_quando_ha_outro_fiscal_permitido(
    controller, contrato, fiscal_ativo, repo_usuario, gestor
):
    segundo_fiscal = repo_usuario.salvar(
        Usuario(
            id=0,
            nome="Segundo Fiscal",
            cpf="22233344455",
            email="segundo@email.com",
            login="segundo",
            senha_hash="hash",
            perfil=Perfil.FISCAL,
            ativo=True,
        )
    )

    controller.vincular(gestor, contrato.numero, fiscal_ativo.id)
    controller.vincular(gestor, contrato.numero, segundo_fiscal.id)

    # Agora pode desvincular um deles pois ainda resta outro fiscal
    controller.desvincular(gestor, contrato.numero, fiscal_ativo.id)

    contrato_atualizado = controller.buscar_por_numero(gestor, contrato.numero)
    assert fiscal_ativo.id not in contrato_atualizado.usuarios_vinculados
    assert segundo_fiscal.id in contrato_atualizado.usuarios_vinculados


def test_rn08_3_usuario_em_mais_de_um_contrato(
    controller, contrato, funcionario_ativo, gestor
):
    outro_contrato = controller.adicionar(gestor,
        DadosCadastroContrato(
            numero="CT-2026-002",
            empresa_contratada="Empresa Beta Ltda",
            vigencia_inicio="01/01/2026",
            vigencia_fim="31/12/2026",
        )
    )

    controller.vincular(gestor, contrato.numero, funcionario_ativo.id)
    controller.vincular(gestor, outro_contrato.numero, funcionario_ativo.id)

    resultado = controller.listar(gestor, id_usuario=funcionario_ativo.id)
    assert len(resultado.itens) == 2
    numeros = {c.numero for c in resultado.itens}
    assert numeros == {"CT-2026-001", "CT-2026-002"}
