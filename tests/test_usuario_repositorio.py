"""Contrato de UsuarioRepositorio.

Toda implementação deve passar nestes testes (Liskov): para cobrir uma nova,
basta incluí-la na fixture `repositorio_implementacao`.
"""
from datetime import datetime

import pytest

from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.persistencia_error import EscritaPersistenciaError
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
    return Usuario(0, "Maria", cpf, email, login, "hash", Perfil.GESTOR)


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


def test_deve_buscar_por_login(repositorio_implementacao):
    salvo = repositorio_implementacao.salvar(novo_usuario())
    assert repositorio_implementacao.buscar_por_login("maria") == salvo
    assert repositorio_implementacao.buscar_por_login("joao") is None


def test_deve_preservar_a_data_do_aceite_dos_termos(repositorio_implementacao):
    momento = datetime(2026, 10, 28, 14, 30, 5)
    usuario = novo_usuario()
    usuario.aceite_termos_em = momento
    repositorio_implementacao.salvar(usuario)
    assert repositorio_implementacao.listar_todos()[0].aceite_termos_em == momento


@pytest.mark.parametrize("login_buscado", ["maria", "MARIA", "Maria"])
def test_deve_buscar_por_login_sem_diferenciar_maiusculas(
        repositorio_implementacao, login_buscado):
    salvo = repositorio_implementacao.salvar(novo_usuario(login="Maria"))

    assert repositorio_implementacao.buscar_por_login(login_buscado) == salvo


def test_deve_buscar_por_login_com_letra_acentuada_sem_diferenciar_maiusculas(
        repositorio_implementacao):
    salvo = repositorio_implementacao.salvar(novo_usuario(login="José"))

    assert repositorio_implementacao.buscar_por_login("JOSÉ") == salvo


@pytest.mark.parametrize("repetido", [
    {"cpf": "12345678900"},
    {"email": "maria@email.com"},
    {"login": "maria"},
], ids=["cpf", "email", "login"])
def test_deve_recusar_cpf_email_ou_login_repetido(
        repositorio_implementacao, repetido):
    repositorio_implementacao.salvar(novo_usuario())
    outro = {"cpf": "98765432100", "email": "joao@email.com", "login": "joao"}
    outro.update(repetido)

    with pytest.raises(EscritaPersistenciaError):
        repositorio_implementacao.salvar(novo_usuario(**outro))

    assert len(repositorio_implementacao.listar_todos()) == 1
