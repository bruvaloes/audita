"""Testes do agrupamento dos receptores da fachada (Issue #25, C4)."""
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock

import pytest

from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController
from controle.receptores_fachada import ReceptoresFachada
from controle.relatorio_controller import RelatorioController
from controle.usuario_controller import UsuarioController
from negocio.evidencia_repositorio import EvidenciaRepositorio


def test_receptores_padrao_devem_vir_vazios():
    receptores = ReceptoresFachada()

    assert (receptores.usuario_controller,
            receptores.autenticacao_controller,
            receptores.contrato_controller,
            receptores.relatorio_controller,
            receptores.evidencia_repositorio) == (None, None, None, None, None)


def test_receptores_devem_guardar_os_controllers_informados():
    usuarios = MagicMock(spec=UsuarioController)
    autenticacao = MagicMock(spec=AutenticacaoController)
    contratos = MagicMock(spec=ContratoController)
    relatorios = MagicMock(spec=RelatorioController)
    evidencias = MagicMock(spec=EvidenciaRepositorio)

    receptores = ReceptoresFachada(
        usuario_controller=usuarios,
        autenticacao_controller=autenticacao,
        contrato_controller=contratos,
        relatorio_controller=relatorios,
        evidencia_repositorio=evidencias,
    )

    assert receptores.usuario_controller is usuarios
    assert receptores.autenticacao_controller is autenticacao
    assert receptores.contrato_controller is contratos
    assert receptores.relatorio_controller is relatorios
    assert receptores.evidencia_repositorio is evidencias


def test_receptores_devem_aceitar_so_parte_dos_controllers():
    contratos = MagicMock(spec=ContratoController)

    receptores = ReceptoresFachada(contrato_controller=contratos)

    assert receptores.contrato_controller is contratos
    assert receptores.usuario_controller is None


def test_receptores_nao_devem_mudar_depois_de_criados():
    receptores = ReceptoresFachada()

    with pytest.raises(FrozenInstanceError):
        receptores.contrato_controller = MagicMock(spec=ContratoController)
