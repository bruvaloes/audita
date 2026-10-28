import pytest

from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
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
def controller(repositorio, hash_senha):
    return UsuarioController(
        repositorio, ValidadorCadastroUsuario(repositorio), hash_senha)


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
    )
