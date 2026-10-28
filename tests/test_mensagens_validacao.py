"""NF001 de Usabilidade: toda mensagem de validação cita o campo e a regra,
tem no máximo 120 caracteres e nunca é genérica.

As mensagens de senha são verificadas em test_senha_usuario.py."""
from dataclasses import replace

import pytest

from excecao.validacao_error import ValidacaoError

LIMITE_MENSAGEM = 120
MENSAGENS_GENERICAS = ("erro", "dados inválidos", "inválido.")

CENARIOS = [
    ({"nome": " "}, "nome"),
    ({"nome": "a" * 101}, "Nome"),
    ({"cpf": "123"}, "CPF"),
    ({"cpf": "52998224726"}, "CPF"),
    ({"email": "maria.email.com"}, "E-mail"),
    ({"email": "a" * 91 + "@email.com"}, "E-mail"),
    ({"login": ""}, "Login"),
    ({"login": "a" * 13}, "Login"),
    ({"login": "ana2"}, "Login"),
    ({"perfil": "ADMIN"}, "Perfil"),
]


@pytest.mark.parametrize("campos, campo_citado", CENARIOS)
def test_mensagem_deve_citar_o_campo_e_caber_no_limite(
        controller, dados_validos, campos, campo_citado):
    with pytest.raises(ValidacaoError) as erro:
        controller.adicionar(replace(dados_validos, **campos))
    mensagem = str(erro.value)
    assert campo_citado in mensagem
    assert len(mensagem) <= LIMITE_MENSAGEM
    assert mensagem.strip().lower() not in MENSAGENS_GENERICAS


def test_mensagem_de_perfil_nao_deve_repetir_o_texto_digitado(
        controller, dados_validos):
    with pytest.raises(ValidacaoError) as erro:
        controller.adicionar(replace(dados_validos, perfil="X" * 500))
    assert len(str(erro.value)) <= LIMITE_MENSAGEM
    assert "XXXX" not in str(erro.value)


@pytest.mark.parametrize("campos, esperada", [
    ({"login": "ana2"}, "Login: use até 12 caracteres, sem números"),
    ({"email": "x"}, "E-mail: use o formato nome@dominio, com até 100 caracteres"),
    ({"perfil": "ADMIN"}, "Perfil: use um destes valores: GESTOR, FISCAL, "
                          "FUNCIONARIO"),
])
def test_mensagens_devem_seguir_o_documento_de_requisitos(
        controller, dados_validos, campos, esperada):
    with pytest.raises(ValidacaoError) as erro:
        controller.adicionar(replace(dados_validos, **campos))
    assert str(erro.value) == esperada
