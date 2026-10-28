from dataclasses import replace

import pytest

from entidade.perfil import Perfil
from excecao.validacao_error import (
    CampoObrigatorioError,
    CpfInvalidoError,
    EmailInvalidoError,
    PerfilInvalidoError,
    UsuarioDuplicadoError,
    ValidacaoError,
)


def test_deve_cadastrar_usuario_com_dados_validos(controller, dados_validos):
    usuario = controller.adicionar(dados_validos)

    assert usuario.id == 1
    assert usuario.perfil == Perfil.GESTOR
    assert controller.listar_todos() == [usuario]


def test_deve_aceitar_perfil_em_minusculas(controller, dados_validos):
    usuario = controller.adicionar(replace(dados_validos, perfil="fiscal"))
    assert usuario.perfil == Perfil.FISCAL


@pytest.mark.parametrize("campo", ["nome", "cpf", "email", "senha", "perfil"])
def test_deve_lancar_erro_quando_campo_obrigatorio_vazio(
        controller, dados_validos, campo):
    with pytest.raises(CampoObrigatorioError):
        controller.adicionar(replace(dados_validos, **{campo: "  "}))


@pytest.mark.parametrize("cpf", [
    "123", "1234567890a", "123456789000",  # tamanho ou caractere inválido
    "52998224726",                         # dígito verificador incorreto
    "11111111111",                         # todos os dígitos iguais
])
def test_deve_lancar_erro_quando_cpf_invalido(controller, dados_validos, cpf):
    with pytest.raises(CpfInvalidoError):
        controller.adicionar(replace(dados_validos, cpf=cpf))


def test_deve_aceitar_cpf_formatado_e_salvar_so_os_numeros(
        controller, dados_validos):
    usuario = controller.adicionar(replace(dados_validos, cpf="529.982.247-25"))
    assert usuario.cpf == "52998224725"


def test_deve_lancar_erro_quando_email_sem_arroba(controller, dados_validos):
    with pytest.raises(EmailInvalidoError):
        controller.adicionar(replace(dados_validos, email="maria.email.com"))


def test_deve_lancar_erro_quando_perfil_invalido(controller, dados_validos):
    with pytest.raises(PerfilInvalidoError):
        controller.adicionar(replace(dados_validos, perfil="ADMIN"))


def test_deve_lancar_erro_quando_cpf_ja_cadastrado(controller, dados_validos):
    controller.adicionar(dados_validos)
    outro = replace(dados_validos, email="outro@email.com")
    with pytest.raises(UsuarioDuplicadoError) as erro:
        controller.adicionar(outro)
    assert str(erro.value) == "CPF já cadastrado"


def test_deve_detectar_cpf_duplicado_em_formato_diferente(
        controller, dados_validos):
    controller.adicionar(dados_validos)
    outro = replace(dados_validos, cpf="529.982.247-25",
                    email="outro@email.com")
    with pytest.raises(UsuarioDuplicadoError):
        controller.adicionar(outro)
    assert len(controller.listar_todos()) == 1


def test_deve_lancar_erro_quando_email_ja_cadastrado(
        controller, dados_validos):
    controller.adicionar(dados_validos)
    outro = replace(dados_validos, cpf="98765432100")
    with pytest.raises(UsuarioDuplicadoError, match="E-mail"):
        controller.adicionar(outro)


def test_todos_os_erros_de_cadastro_herdam_de_validacao_error():
    for erro in (CampoObrigatorioError, CpfInvalidoError, EmailInvalidoError,
                 PerfilInvalidoError, UsuarioDuplicadoError):
        assert issubclass(erro, ValidacaoError)
