"""Contrato de UsuarioRepositorio.

Toda implementação deve passar nestes testes (Liskov): para cobrir uma nova,
basta incluí-la na fixture `repositorio_implementacao`.
"""
import pytest

from entidade.perfil import Perfil
from entidade.usuario import Usuario
from persistencia.usuario_repositorio import UsuarioRepositorio
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio_implementacao(request, tmp_path) -> UsuarioRepositorio:
    if request.param == "memoria":
        return UsuarioRepositorioMemoria()
    return UsuarioRepositorioSQLite(str(tmp_path / "contrato.db"))


def novo_usuario(cpf="12345678900", email="maria@email.com",
                 login="maria") -> Usuario:
    return Usuario(0, "Maria", cpf, email, login, "senha", Perfil.GESTOR)


def test_deve_atribuir_ids_sequenciais_ao_salvar(repositorio_implementacao):
    primeiro = repositorio_implementacao.salvar(novo_usuario())
    segundo = repositorio_implementacao.salvar(
        novo_usuario("98765432100", "joao@email.com", "joao"))

    assert (primeiro.id, segundo.id) == (1, 2)


def test_deve_listar_na_ordem_em_que_foram_salvos(repositorio_implementacao):
    primeiro = repositorio_implementacao.salvar(novo_usuario())
    segundo = repositorio_implementacao.salvar(
        novo_usuario("98765432100", "joao@email.com", "joao"))

    assert repositorio_implementacao.listar_todos() == [primeiro, segundo]


def test_deve_buscar_por_cpf_e_por_email(repositorio_implementacao):
    usuario = repositorio_implementacao.salvar(novo_usuario())

    assert repositorio_implementacao.buscar_por_cpf(usuario.cpf) == usuario
    assert repositorio_implementacao.buscar_por_email(usuario.email) == usuario


def test_deve_retornar_none_quando_nao_encontrar(repositorio_implementacao):
    assert repositorio_implementacao.buscar_por_cpf("00000000000") is None
    assert repositorio_implementacao.buscar_por_email("x@y.com") is None
