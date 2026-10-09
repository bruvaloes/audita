import pytest

from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria


@pytest.fixture
def repositorio():
    return UsuarioRepositorioMemoria()


@pytest.fixture
def controller(repositorio):
    return UsuarioController(repositorio, ValidadorCadastroUsuario(repositorio))


@pytest.fixture
def dados_validos():
    return DadosCadastroUsuario(
        nome="Maria",
        cpf="12345678900",
        email="maria@email.com",
        login="maria",
        senha="Senha@123",
        perfil="GESTOR",
    )
