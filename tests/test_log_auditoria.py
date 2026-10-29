"""Testes do Adapter para biblioteca de log e do log de auditoria (NF004).

Cobre:
- Interface de log própria (LogAuditoria) e padrão Adapter (LogAuditoriaAdapter)
- Implementação em memória (LogAuditoriaMemoria) para testes e persistência volátil
- Registro de ações críticas: CADASTRO, EDICAO, EXCLUSAO e VALIDACAO
- Imutabilidade dos registros de auditoria (sem métodos para alterar ou apagar)
- Formato padronizado de data e hora: dd/mm/aaaa hh:mm:ss
- Troca transparente de biblioteca/implementação sem impacto no controller
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime
from pathlib import Path

import pytest

from controle.usuario_controller import UsuarioController
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from log.log_auditoria import LogAuditoria
from log.log_auditoria_adapter import LogAuditoriaAdapter
from log.log_auditoria_memoria import LogAuditoriaMemoria
from log.operacao_log import OperacaoLog
from log.registro_log import RegistroLog


@pytest.fixture
def momento():
    return datetime(2026, 10, 28, 14, 30, 5)


@pytest.fixture(params=["memoria", "adapter"])
def log_implementacao(request, tmp_path) -> LogAuditoria:
    """Fixture que roda os testes principais contra ambas as implementações (Liskov)."""
    if request.param == "memoria":
        yield LogAuditoriaMemoria()
    else:
        caminho = tmp_path / "auditoria_teste.log"
        adapter = LogAuditoriaAdapter(caminho_arquivo=str(caminho))
        yield adapter
        adapter.fechar()


# --- Testes de cada tipo de ação crítica (NF004) ---


def test_acao_cadastro_gera_registro_esperado(log_implementacao, momento):
    registro = RegistroLog(
        usuario="gestor1",
        operacao=OperacaoLog.CADASTRO,
        data_hora=momento,
        detalhes="Contrato CT-2026-001 cadastrado",
    )
    log_implementacao.registrar(registro)

    registros = log_implementacao.listar()
    assert len(registros) == 1
    assert registros[0].operacao == OperacaoLog.CADASTRO
    assert registros[0].usuario == "gestor1"
    assert registros[0].data_hora_formatada == "28/10/2026 14:30:05"
    assert "CT-2026-001" in registros[0].detalhes


def test_acao_edicao_com_valor_anterior_e_novo(log_implementacao, momento):
    registro = RegistroLog(
        usuario="gestor1",
        operacao=OperacaoLog.EDICAO,
        data_hora=momento,
        detalhes="Contrato CT-2026-001 alterado: anterior={'vigencia': '31/12/2026'} | novo={'vigencia': '31/12/2027'}",
    )
    log_implementacao.registrar(registro)

    registros = log_implementacao.listar()
    assert len(registros) == 1
    assert registros[0].operacao == OperacaoLog.EDICAO
    assert "anterior=" in registros[0].detalhes
    assert "novo=" in registros[0].detalhes


def test_acao_exclusao_gera_registro_esperado(log_implementacao, momento):
    registro = RegistroLog(
        usuario="gestor1",
        operacao=OperacaoLog.EXCLUSAO,
        data_hora=momento,
        detalhes="Contrato CT-2026-001 removido sem evidencias vinculadas",
    )
    log_implementacao.registrar(registro)

    registros = log_implementacao.listar()
    assert len(registros) == 1
    assert registros[0].operacao == OperacaoLog.EXCLUSAO
    assert "removido" in registros[0].detalhes


def test_acao_validacao_gera_registro_esperado(log_implementacao, momento):
    registro = RegistroLog(
        usuario="fiscal1",
        operacao=OperacaoLog.VALIDACAO,
        data_hora=momento,
        detalhes="Evidencia EV-001 validada: situacao alterada para APROVADA",
    )
    log_implementacao.registrar(registro)

    registros = log_implementacao.listar()
    assert len(registros) == 1
    assert registros[0].operacao == OperacaoLog.VALIDACAO
    assert "APROVADA" in registros[0].detalhes


# --- Teste de integração do log com Controller real (UsuarioController) ---


def test_usuario_controller_registra_cadastro_no_log_de_auditoria(
    repositorio, hash_senha, momento, dados_validos
):
    log = LogAuditoriaMemoria()
    controller = UsuarioController(
        repositorio=repositorio,
        validador=ValidadorCadastroUsuario(repositorio),
        hash_senha=hash_senha,
        relogio=lambda: momento,
        log=log,
    )

    controller.adicionar(dados_validos)

    registros = log.listar()
    assert len(registros) == 1
    assert registros[0].usuario == dados_validos.login
    assert registros[0].operacao == OperacaoLog.CADASTRO
    assert registros[0].data_hora == momento
    assert dados_validos.login in registros[0].detalhes


# --- Testes de Imutabilidade (NF004) ---


def test_registro_log_e_imutavel(momento):
    registro = RegistroLog(
        usuario="maria",
        operacao=OperacaoLog.CADASTRO,
        data_hora=momento,
        detalhes="Cadastro efetuado",
    )

    with pytest.raises(FrozenInstanceError):
        registro.usuario = "joao"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        registro.detalhes = "Tentativa de alteracao"  # type: ignore[misc]


def test_log_auditoria_nao_possui_metodos_para_alterar_nem_apagar():
    """A interface e as implementações não devem ter nenhuma operação de alteração ou deleção."""
    metodos_proibidos = [
        "alterar",
        "editar",
        "atualizar",
        "modificar",
        "apagar",
        "excluir",
        "remover",
        "delete",
        "limpar",
    ]

    for classe in [LogAuditoria, LogAuditoriaMemoria, LogAuditoriaAdapter]:
        for metodo in metodos_proibidos:
            assert not hasattr(classe, metodo), (
                f"A classe {classe.__name__} não deve ter o método imutável '{metodo}' (NF004)"
            )


# --- Teste de Formatação de Data e Hora (NF004) ---


def test_formato_data_hora_dd_mm_aaaa_hh_mm_ss():
    data_hora = datetime(2026, 10, 28, 9, 5, 2)
    registro = RegistroLog(
        usuario="fiscal",
        operacao=OperacaoLog.VALIDACAO,
        data_hora=data_hora,
        detalhes="Validado",
    )
    assert registro.data_hora_formatada == "28/10/2026 09:05:02"


# --- Teste do Padrão Adapter (Troca de biblioteca sem impacto no Controller) ---


def test_trocar_implementacao_de_log_nao_muda_controller(
    repositorio, hash_senha, momento, dados_validos, tmp_path
):
    """Garante que o controller pode trabalhar com qualquer implementação de LogAuditoria."""
    log_memoria = LogAuditoriaMemoria()
    controller_memoria = UsuarioController(
        repositorio=repositorio,
        validador=ValidadorCadastroUsuario(repositorio),
        hash_senha=hash_senha,
        relogio=lambda: momento,
        log=log_memoria,
    )
    controller_memoria.adicionar(dados_validos)
    assert len(log_memoria.listar()) == 1

    # Substitui para o Adapter com logging e grava novo usuário
    arquivo_log = tmp_path / "adapter_controller.log"
    log_adapter = LogAuditoriaAdapter(caminho_arquivo=str(arquivo_log))
    try:
        controller_adapter = UsuarioController(
            repositorio=repositorio,
            validador=ValidadorCadastroUsuario(repositorio),
            hash_senha=hash_senha,
            relogio=lambda: momento,
            log=log_adapter,
        )
        dados_segundo = replace(
            dados_validos,
            cpf="11144477735",
            login="mariana",
            email="mariana@email.com",
        )

        controller_adapter.adicionar(dados_segundo)

        registros_adapter = log_adapter.listar()
        assert len(registros_adapter) == 1
        assert registros_adapter[0].usuario == "mariana"
        assert registros_adapter[0].operacao == OperacaoLog.CADASTRO
    finally:
        log_adapter.fechar()


# --- Teste específico do Adapter com biblioteca logging ---


def test_adapter_persiste_registros_em_arquivo_com_logging(tmp_path, momento):
    arquivo = tmp_path / "auditoria.log"
    adapter = LogAuditoriaAdapter(caminho_arquivo=str(arquivo))

    try:
        r1 = RegistroLog("user1", OperacaoLog.CADASTRO, momento, "Criado")
        r2 = RegistroLog(None, OperacaoLog.VALIDACAO, momento, "Validado anonimamente")

        adapter.registrar(r1)
        adapter.registrar(r2)

        # Confere que o arquivo físico existe e tem conteúdo gravado
        assert arquivo.exists()
        conteudo = arquivo.read_text(encoding="utf-8")
        assert "CADASTRO" in conteudo
        assert "user1" in conteudo
        assert "VALIDACAO" in conteudo

        # Confere que listar() reconstrói os registros com fidelidade
        registros = adapter.listar()
        assert len(registros) == 2
        assert registros[0].usuario == "user1"
        assert registros[0].operacao == OperacaoLog.CADASTRO
        assert registros[1].usuario is None
        assert registros[1].operacao == OperacaoLog.VALIDACAO
    finally:
        adapter.fechar()
