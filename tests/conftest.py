from datetime import datetime

import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.autenticacao_controller import AutenticacaoController
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
from controle.sessao import Sessao
from fronteira.painel_fronteira import PainelFronteira
from persistencia.acesso_repositorio_memoria import AcessoRepositorioMemoria
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria


@pytest.fixture
def repositorio():
    return UsuarioRepositorioMemoria()


@pytest.fixture
def hash_senha():
    # Custos mínimos só para os testes não ficarem lentos; o padrão de produção
    # é verificado em test_hash_senha.py.
    return HashSenhaArgon2(custo_tempo=1, custo_memoria_kib=8, paralelismo=1)


@pytest.fixture
def controle_acesso():
    return ControleAcesso()


@pytest.fixture
def sessao():
    return Sessao()


@pytest.fixture
def painel(sessao, controle_acesso):
    return PainelFronteira(sessao, controle_acesso)


@pytest.fixture
def controller(repositorio, hash_senha, controle_acesso):
    return UsuarioController(
        repositorio, ValidadorCadastroUsuario(repositorio), hash_senha,
        controle_acesso)


@pytest.fixture
def acessos():
    return AcessoRepositorioMemoria()


@pytest.fixture
def momento():
    return datetime(2026, 10, 28, 14, 30, 5)


@pytest.fixture
def autenticacao(repositorio, acessos, hash_senha, momento):
    return AutenticacaoController(
        repositorio, acessos, hash_senha, relogio=lambda: momento)


@pytest.fixture
def dados_validos():
    return DadosCadastroUsuario(
        nome="Maria",
        cpf="52998224725",
        email="maria@email.com",
        login="maria",
        senha="Senha@123",
        confirmacao_senha="Senha@123",
        perfil="GESTOR",
        aceite_termos="s",
    )
