import sqlite3

import pytest

from controle.seguranca.hash_senha_argon2 import HashSenhaArgon2
from persistencia.usuario_repositorio_sqlite import UsuarioRepositorioSQLite

SENHA = "Senha@123"


def test_deve_usar_argon2id_com_os_custos_padrao():
    hash_senha = HashSenhaArgon2().gerar(SENHA)
    assert hash_senha.startswith("$argon2id$")
    assert "m=65536,t=3,p=4" in hash_senha


def test_deve_gerar_hashes_diferentes_para_a_mesma_senha(hash_senha):
    assert hash_senha.gerar(SENHA) != hash_senha.gerar(SENHA)


def test_deve_verificar_senha_correta_e_recusar_a_errada(hash_senha):
    gerado = hash_senha.gerar(SENHA)
    assert hash_senha.verificar(SENHA, gerado) is True
    assert hash_senha.verificar("Senha@124", gerado) is False


def test_deve_recusar_hash_invalido_sem_levantar_erro(hash_senha):
    assert hash_senha.verificar(SENHA, "isto-nao-e-um-hash") is False


def test_deve_aceitar_senha_no_tamanho_maximo_sem_truncar(hash_senha):
    senha = "Aa1!" + "b" * 124
    gerado = hash_senha.gerar(senha)
    assert hash_senha.verificar(senha, gerado) is True
    assert hash_senha.verificar(senha[:72], gerado) is False


def test_controller_deve_salvar_apenas_o_hash(controller, dados_validos):
    usuario = controller.adicionar(dados_validos)
    assert usuario.senha_hash != dados_validos.senha
    assert usuario.senha_hash.startswith("$argon2id$")


def test_representacoes_nao_devem_expor_senha_nem_hash(controller, dados_validos):
    usuario = controller.adicionar(dados_validos)
    for texto in (repr(usuario), str(usuario)):
        assert dados_validos.senha not in texto
        assert usuario.senha_hash not in texto


def test_banco_nao_deve_conter_a_senha_em_texto_aberto(
        controller, dados_validos, tmp_path):
    from controle.usuario_controller import UsuarioController
    from controle.validacao.validador_cadastro_usuario import (
        ValidadorCadastroUsuario,
    )
    caminho = str(tmp_path / "hash.db")
    repositorio = UsuarioRepositorioSQLite(caminho)
    sqlite_controller = UsuarioController(
        repositorio, ValidadorCadastroUsuario(repositorio),
        HashSenhaArgon2(custo_tempo=1, custo_memoria_kib=8, paralelismo=1))

    sqlite_controller.adicionar(dados_validos)

    with sqlite3.connect(caminho) as conexao:
        (gravado,) = conexao.execute("SELECT senha FROM usuarios").fetchone()
    assert gravado != dados_validos.senha
    assert gravado.startswith("$argon2id$")


@pytest.mark.parametrize("campos", [
    {"senha": "fraca", "confirmacao_senha": "fraca"},
    {"senha": "abcdefgh1", "confirmacao_senha": "abcdefgh1"},
    {"confirmacao_senha": "Outra@123"},
    {"login": "Senha@Forte", "senha": "Senha@Forte",
     "confirmacao_senha": "Senha@Forte"},
])
def test_mensagens_de_erro_nao_devem_conter_a_senha(
        controller, dados_validos, campos):
    from dataclasses import replace

    from excecao.senha_invalida_error import SenhaInvalidaError

    dados = replace(dados_validos, **campos)
    with pytest.raises(SenhaInvalidaError) as erro:
        controller.adicionar(dados)
    assert dados.senha not in str(erro.value)
    assert dados.confirmacao_senha not in str(erro.value)


def test_cadastro_nao_deve_registrar_a_senha_nem_o_hash_em_logs(
        controller, dados_validos, caplog):
    import logging

    with caplog.at_level(logging.DEBUG):
        usuario = controller.adicionar(dados_validos)
    assert dados_validos.senha not in caplog.text
    assert usuario.senha_hash not in caplog.text
