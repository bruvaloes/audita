"""Testes de listagem de contratos (RF 05).

Cobre os critérios de aceite C1 a C4 e regras RN05.1 a RN05.4:
- C1: 45 contratos -> mostra os 20 mais recentes (ordem decrescente) e navegação para pág 2 e 3
- C2: Busca por termo (número ou empresa, case-insensitive)
- C3: Filtro por situação (ENCERRADO, ATIVO)
- C4: Busca sem correspondência -> nenhum contrato encontrado
- RN05.2: Ordenação decrescente por vigência_inicio
"""
from datetime import date
import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from entidade.contrato import Contrato
from entidade.situacao_contrato import SituacaoContrato
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria


@pytest.fixture
def repo():
    return ContratoRepositorioMemoria()


@pytest.fixture
def controller(repo):
    return ContratoController(
        repositorio=repo, controle_acesso=ControleAcesso())


def test_c1_listagem_45_contratos_paginacao_e_ordenacao(controller, repo, gestor):
    # Cadastra 45 contratos com datas variadas
    for i in range(1, 46):
        dia = (i % 28) + 1
        mes = ((i // 28) % 12) + 1
        ano = 2020 + (i // 5)
        contrato = Contrato(
            id=0,
            numero=f"CT-{i:03d}",
            empresa_contratada=f"Empresa {i}",
            vigencia_inicio=date(ano, mes, dia),
            vigencia_fim=date(ano + 1, mes, dia),
            arquivo=None,
            situacao=SituacaoContrato.ATIVO,
        )
        repo.salvar(contrato)

    # Página 1
    p1 = controller.listar(gestor, pagina=1, por_pagina=20)
    assert len(p1.itens) == 20
    assert p1.total_paginas == 3
    assert p1.total_itens == 45

    # RN05.2: Garantir que os itens estão ordenados pela data mais recente primeiro
    datas_p1 = [c.vigencia_inicio for c in p1.itens]
    assert datas_p1 == sorted(datas_p1, reverse=True)

    # Página 2
    p2 = controller.listar(gestor, pagina=2, por_pagina=20)
    assert len(p2.itens) == 20
    assert p2.total_paginas == 3

    # Página 3
    p3 = controller.listar(gestor, pagina=3, por_pagina=20)
    assert len(p3.itens) == 5
    assert p3.total_paginas == 3


def test_c2_busca_por_termo_no_numero_ou_empresa(controller, repo, gestor):
    repo.salvar(
        Contrato(
            id=0,
            numero="CT-LIMPEZA-01",
            empresa_contratada="Alvorada Servicos",
            vigencia_inicio=date(2026, 1, 1),
            vigencia_fim=date(2026, 12, 31),
            arquivo=None,
            situacao=SituacaoContrato.ATIVO,
        )
    )
    repo.salvar(
        Contrato(
            id=0,
            numero="CT-MANUT-02",
            empresa_contratada="Limpeza Total Ltda",
            vigencia_inicio=date(2026, 2, 1),
            vigencia_fim=date(2026, 12, 31),
            arquivo=None,
            situacao=SituacaoContrato.ATIVO,
        )
    )
    repo.salvar(
        Contrato(
            id=0,
            numero="CT-SEG-03",
            empresa_contratada="Vigilancia Alpha",
            vigencia_inicio=date(2026, 3, 1),
            vigencia_fim=date(2026, 12, 31),
            arquivo=None,
            situacao=SituacaoContrato.ATIVO,
        )
    )

    resultado = controller.listar(gestor, busca="limpeza")
    assert len(resultado.itens) == 2
    numeros = {c.numero for c in resultado.itens}
    assert numeros == {"CT-LIMPEZA-01", "CT-MANUT-02"}


def test_c3_filtro_por_situacao_encerrado(controller, repo, gestor):
    repo.salvar(
        Contrato(
            id=0,
            numero="CT-ATIVO-01",
            empresa_contratada="Empresa A",
            vigencia_inicio=date(2026, 1, 1),
            vigencia_fim=date(2026, 12, 31),
            arquivo=None,
            situacao=SituacaoContrato.ATIVO,
        )
    )
    repo.salvar(
        Contrato(
            id=0,
            numero="CT-ENCERRADO-02",
            empresa_contratada="Empresa B",
            vigencia_inicio=date(2025, 1, 1),
            vigencia_fim=date(2025, 12, 31),
            arquivo=None,
            situacao=SituacaoContrato.ENCERRADO,
        )
    )

    resultado = controller.listar(gestor, situacao="ENCERRADO")
    assert len(resultado.itens) == 1
    assert resultado.itens[0].numero == "CT-ENCERRADO-02"
    assert resultado.itens[0].situacao == SituacaoContrato.ENCERRADO


def test_c4_busca_sem_resultado(controller, repo, gestor):
    repo.salvar(
        Contrato(
            id=0,
            numero="CT-001",
            empresa_contratada="Empresa A",
            vigencia_inicio=date(2026, 1, 1),
            vigencia_fim=date(2026, 12, 31),
            arquivo=None,
            situacao=SituacaoContrato.ATIVO,
        )
    )

    resultado = controller.listar(gestor, busca="termo-inexistente")
    assert len(resultado.itens) == 0
    assert resultado.total_itens == 0
    assert resultado.total_paginas == 0


def test_c5_situacao_invalida_deve_levantar_erro_de_validacao(controller, gestor):
    from excecao.validacao_error import SituacaoInvalidaError, ValidacaoError

    with pytest.raises(SituacaoInvalidaError) as erro:
        controller.listar(gestor, situacao="XYZ")

    assert isinstance(erro.value, ValidacaoError)
    assert str(erro.value) == "Situação: use um destes valores: ATIVO, ENCERRADO"


def test_contar_deve_devolver_a_quantidade_de_contratos(controller, gestor):
    assert controller.contar() == 0

    for numero in ("CT-1", "CT-2", "CT-3"):
        controller.adicionar(gestor, DadosCadastroContrato(
            numero=numero, empresa_contratada="Empresa",
            vigencia_inicio="01/01/2026", vigencia_fim="31/12/2026"))

    assert controller.contar() == 3
