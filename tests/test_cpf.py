import pytest

from controle.validacao.validador_cpf import ValidadorCpf
from entidade.cpf import cpf_valido, mascarar_cpf, normalizar_cpf
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.validacao_error import CpfInvalidoError

CPF_VALIDO = "52998224725"
CPF_FORMATADO = "529.982.247-25"


@pytest.mark.parametrize("texto, esperado", [
    (CPF_FORMATADO, CPF_VALIDO),
    (f"  {CPF_FORMATADO} ", CPF_VALIDO),
    (CPF_VALIDO, CPF_VALIDO),
])
def test_normalizar_cpf_deve_deixar_so_os_digitos(texto, esperado):
    assert normalizar_cpf(texto) == esperado


@pytest.mark.parametrize("cpf", [
    CPF_VALIDO, CPF_FORMATADO, "11144477735", "123.456.789-09", "39053344705",
])
def test_deve_aceitar_cpf_valido_com_ou_sem_pontuacao(cpf):
    assert cpf_valido(cpf) is True
    ValidadorCpf().validar(cpf)


@pytest.mark.parametrize("cpf", [
    "52998224726",     # primeiro dígito verificador correto, segundo errado
    "52998224735",     # primeiro dígito verificador errado
    "12345678900",
])
def test_deve_rejeitar_cpf_com_digito_verificador_incorreto(cpf):
    with pytest.raises(CpfInvalidoError):
        ValidadorCpf().validar(cpf)


@pytest.mark.parametrize("digito", "0123456789")
def test_deve_rejeitar_cpf_com_todos_os_digitos_iguais(digito):
    with pytest.raises(CpfInvalidoError):
        ValidadorCpf().validar(digito * 11)


@pytest.mark.parametrize("cpf", ["", "123", "5299822472", "529982247250",
                                 "5299822472a", "abc.def.ghi-jk"])
def test_deve_rejeitar_cpf_com_tamanho_ou_caractere_invalido(cpf):
    with pytest.raises(CpfInvalidoError):
        ValidadorCpf().validar(cpf)


def test_mensagem_de_cpf_invalido():
    with pytest.raises(CpfInvalidoError) as erro:
        ValidadorCpf().validar("123")
    assert str(erro.value) == "CPF inválido"


@pytest.mark.parametrize("cpf", [CPF_VALIDO, CPF_FORMATADO])
def test_mascarar_cpf_deve_ocultar_primeiros_3_e_ultimos_2_digitos(cpf):
    assert mascarar_cpf(cpf) == "XXX.982.247-XX"


@pytest.mark.parametrize("cpf", ["", "123", "abc"])
def test_mascarar_cpf_malformado_nao_deve_vazar_nada(cpf):
    assert mascarar_cpf(cpf) == "XXX.XXX.XXX-XX"


def test_representacoes_do_usuario_nao_devem_conter_o_cpf_completo():
    usuario = Usuario(1, "Maria", CPF_VALIDO, "m@x.com", "maria", "hash",
                      Perfil.GESTOR)
    for texto in (repr(usuario), str(usuario)):
        assert CPF_VALIDO not in texto
        assert CPF_FORMATADO not in texto
    assert "XXX.982.247-XX" in repr(usuario)
