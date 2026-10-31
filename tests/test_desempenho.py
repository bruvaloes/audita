"""NF001 de Desempenho: cadastro, listagem, edição e remoção respondem em até
1 segundo na maioria das requisições, com o volume de referência carregado.

Métrica do documento de requisitos: pelo menos 95% das requisições em até
1 segundo e nenhuma acima de 3 segundos, com 100 usuários e 50 contratos.
Verificação: 100 execuções de cada operação, nos dois mecanismos de
persistência.
"""
import time
from datetime import datetime

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.contrato_controller import ContratoController
from controle.dados_cadastro_contrato import DadosCadastroContrato
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from persistencia.contrato_repositorio_memoria import ContratoRepositorioMemoria
from persistencia.contrato_repositorio_sqlite import ContratoRepositorioSQLite
from persistencia.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from persistencia.evidencia_repositorio_sqlite import EvidenciaRepositorioSQLite
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite

USUARIOS_DE_REFERENCIA = 100
CONTRATOS_DE_REFERENCIA = 50
EXECUCOES = 100
LIMITE_COMUM = 1.0
LIMITE_ABSOLUTO = 3.0
PROPORCAO_MINIMA = 0.95


def cpf_valido(indice: int) -> str:
    base = f"{indice + 100000000:09d}"
    for tamanho in (9, 10):
        pesos = range(tamanho + 1, 1, -1)
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        base += str((soma * 10 % 11) % 10)
    return base


def letras(indice: int) -> str:
    """Login sem números: 0 -> 'aa', 1 -> 'ab' ..."""
    return "u" + chr(97 + indice // 26 % 26) + chr(97 + indice % 26)


def dados_usuario(indice: int) -> DadosCadastroUsuario:
    return DadosCadastroUsuario(
        nome=f"Usuario {indice}", cpf=cpf_valido(indice),
        email=f"usuario{indice}@email.com", login=letras(indice),
        senha="Senha@123", confirmacao_senha="Senha@123",
        perfil="FUNCIONARIO", aceite_termos="s")


def dados_contrato(indice: int, empresa: str = "Empresa Alpha Ltda"):
    return DadosCadastroContrato(
        numero=f"CT-{indice:04d}", empresa_contratada=empresa,
        vigencia_inicio="01/01/2026", vigencia_fim="31/12/2026")


def medir(operacao, execucoes=EXECUCOES) -> list[float]:
    tempos = []
    for i in range(execucoes):
        inicio = time.perf_counter()
        operacao(i)
        tempos.append(time.perf_counter() - inicio)
    return tempos


def conferir(nome: str, tempos: list[float]) -> None:
    dentro = sum(1 for t in tempos if t <= LIMITE_COMUM) / len(tempos)
    assert dentro >= PROPORCAO_MINIMA, (
        f"{nome}: só {dentro:.0%} das execuções em até {LIMITE_COMUM}s")
    assert max(tempos) <= LIMITE_ABSOLUTO, (
        f"{nome}: a mais lenta levou {max(tempos):.2f}s")


@pytest.fixture(params=["memoria", "sqlite"])
def sistema(request, tmp_path):
    if request.param == "memoria":
        usuarios = UsuarioRepositorioMemoria()
        contratos = ContratoRepositorioMemoria()
        evidencias = EvidenciaRepositorioMemoria()
    else:
        banco = str(tmp_path / "desempenho.db")
        usuarios = UsuarioRepositorioSQLite(banco)
        contratos = ContratoRepositorioSQLite(banco)
        evidencias = EvidenciaRepositorioSQLite(banco)
    controle = ControleAcesso()
    # Custo de produção do hash, para o cadastro de usuário ser medido de verdade.
    hash_senha = HashSenhaArgon2()
    usuario_controller = UsuarioController(
        usuarios, ValidadorCadastroUsuario(usuarios), hash_senha, controle,
        relogio=lambda: datetime(2026, 10, 30, 9, 0, 0))
    contrato_controller = ContratoController(
        repositorio=contratos, controle_acesso=controle,
        evidencia_repositorio=evidencias, usuario_repositorio=usuarios)
    gestor = Usuario(0, "Gestor", cpf_valido(999), "gestor@email.com",
                     "gestor", "hash", Perfil.GESTOR)
    # Volume de referência já carregado: 100 usuários e 50 contratos. Os
    # usuários entram direto no repositório; só o teste de cadastro de usuário
    # paga o custo do hash.
    for i in range(USUARIOS_DE_REFERENCIA):
        usuarios.salvar(Usuario(
            0, f"Usuario {i}", cpf_valido(i), f"usuario{i}@email.com",
            letras(i), "hash", Perfil.FUNCIONARIO))
    for i in range(CONTRATOS_DE_REFERENCIA):
        contrato_controller.adicionar(gestor, dados_contrato(i))
    return usuario_controller, contrato_controller, gestor


def test_listar_usuarios_deve_responder_dentro_do_limite(sistema):
    usuarios, _, gestor = sistema
    conferir("listar usuários", medir(lambda i: usuarios.listar_todos(gestor)))


def test_listar_contratos_deve_responder_dentro_do_limite(sistema):
    _, contratos, gestor = sistema
    conferir("listar contratos", medir(lambda i: contratos.listar(gestor)))


def test_editar_contrato_deve_responder_dentro_do_limite(sistema):
    _, contratos, gestor = sistema
    conferir("editar contrato", medir(lambda i: contratos.atualizar(
        gestor, f"CT-{i % CONTRATOS_DE_REFERENCIA:04d}",
        dados_contrato(i % CONTRATOS_DE_REFERENCIA, f"Empresa {i}"))))


def test_cadastrar_e_remover_contrato_devem_responder_dentro_do_limite(sistema):
    _, contratos, gestor = sistema
    base = CONTRATOS_DE_REFERENCIA
    conferir("cadastrar contrato", medir(
        lambda i: contratos.adicionar(gestor, dados_contrato(base + i))))
    conferir("remover contrato", medir(
        lambda i: contratos.remover(
            gestor, f"CT-{base + i:04d}", confirmado=True)))


def test_cadastrar_usuario_deve_responder_dentro_do_limite(sistema):
    usuarios, _, _ = sistema
    base = USUARIOS_DE_REFERENCIA
    conferir("cadastrar usuário", medir(
        lambda i: usuarios.adicionar(dados_usuario(base + i))))
