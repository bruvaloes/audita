"""RF 03 (controle de acesso por perfil) e NF003 de Segurança: a permissão é
conferida no controller, e não só escondida no menu."""
import pytest

from controle.acesso.controle_acesso import ControleAcesso
from controle.acesso.operacao import Operacao
from controle.acesso.permissoes import PERMISSOES_PADRAO
from controle.sessao import Sessao
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.acesso_negado_error import AcessoNegadoError
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.painel_fronteira import AcaoDoPainel, PainelFronteira
from fronteira.usuario_fronteira import UsuarioFronteira

# Matriz da v2.0 (RN03.1 a RN03.3), escrita à parte para o teste não repetir
# o código que está sendo verificado.
ESPERADO = {
    Perfil.GESTOR: {
        Operacao.LISTAR_USUARIOS, Operacao.CADASTRAR_CONTRATO,
        Operacao.LISTAR_CONTRATOS, Operacao.EDITAR_CONTRATO,
        Operacao.REMOVER_CONTRATO, Operacao.VINCULAR_USUARIO_CONTRATO,
        Operacao.LISTAR_EVIDENCIAS, Operacao.VALIDAR_EVIDENCIA,
    },
    Perfil.FISCAL: set(),
    Perfil.FUNCIONARIO: {
        Operacao.REGISTRAR_EVIDENCIA, Operacao.CONSULTAR_PROPRIOS_ENVIOS,
    },
}
COMBINACOES = [(perfil, operacao) for perfil in Perfil for operacao in Operacao]


def usuario_com(perfil: Perfil) -> Usuario:
    return Usuario(1, "Ana", "52998224725", "ana@email.com", "ana", "hash",
                   perfil)


# --- matriz de permissões ---------------------------------------------------

@pytest.mark.parametrize("perfil, operacao", COMBINACOES)
def test_matriz_deve_seguir_o_documento_de_requisitos(
        controle_acesso, perfil, operacao):
    permitida = operacao in ESPERADO[perfil]
    assert controle_acesso.permite(usuario_com(perfil), operacao) is permitida


@pytest.mark.parametrize("perfil, operacao", [
    c for c in COMBINACOES if c[1] in ESPERADO[c[0]]])
def test_c1_deve_permitir_a_operacao_do_perfil(
        controle_acesso, perfil, operacao):
    controle_acesso.verificar(usuario_com(perfil), operacao)


@pytest.mark.parametrize("perfil, operacao", [
    c for c in COMBINACOES if c[1] not in ESPERADO[c[0]]])
def test_c2_deve_negar_operacao_de_outro_perfil(
        controle_acesso, perfil, operacao):
    with pytest.raises(AcessoNegadoError) as erro:
        controle_acesso.verificar(usuario_com(perfil), operacao)
    assert str(erro.value) == "Acesso negado"


@pytest.mark.parametrize("operacao", list(Operacao))
def test_sem_usuario_autenticado_toda_operacao_deve_ser_negada(
        controle_acesso, operacao):
    assert controle_acesso.permite(None, operacao) is False
    with pytest.raises(AcessoNegadoError):
        controle_acesso.verificar(None, operacao)


def test_toda_operacao_deve_ser_permitida_a_pelo_menos_um_perfil():
    permitidas = set().union(*PERMISSOES_PADRAO.values())
    assert permitidas == set(Operacao)


def test_todo_perfil_deve_estar_na_matriz():
    assert set(PERMISSOES_PADRAO) == set(Perfil)


def test_permissoes_devem_ser_trocaveis_sem_mudar_o_codigo():
    so_funcionario_lista = ControleAcesso({
        Perfil.FUNCIONARIO: frozenset({Operacao.LISTAR_USUARIOS})})
    assert so_funcionario_lista.permite(
        usuario_com(Perfil.FUNCIONARIO), Operacao.LISTAR_USUARIOS)
    assert not so_funcionario_lista.permite(
        usuario_com(Perfil.GESTOR), Operacao.LISTAR_USUARIOS)


def test_perfil_fora_da_matriz_deve_ser_negado():
    sem_regras = ControleAcesso({})
    assert not sem_regras.permite(
        usuario_com(Perfil.GESTOR), Operacao.LISTAR_USUARIOS)


# --- controller: a conferência acontece na camada de controle -----------------

def test_controller_deve_listar_usuarios_para_o_gestor(
        controller, dados_validos):
    controller.adicionar(dados_validos)
    usuarios = controller.listar_todos(usuario_com(Perfil.GESTOR))
    assert [u.login for u in usuarios] == ["maria"]


@pytest.mark.parametrize("perfil", [Perfil.FISCAL, Perfil.FUNCIONARIO])
def test_controller_nao_deve_devolver_dados_a_perfil_sem_permissao(
        controller, dados_validos, perfil):
    controller.adicionar(dados_validos)
    with pytest.raises(AcessoNegadoError):
        controller.listar_todos(usuario_com(perfil))


def test_controller_nao_deve_listar_sem_usuario_autenticado(
        controller, dados_validos):
    controller.adicionar(dados_validos)
    with pytest.raises(AcessoNegadoError):
        controller.listar_todos(None)


def test_cadastro_de_usuario_continua_publico(controller, dados_validos):
    assert controller.adicionar(dados_validos).id == 1


# --- sessão ---------------------------------------------------------------

def test_sessao_comeca_sem_usuario():
    assert Sessao().usuario_atual is None


def test_sessao_deve_guardar_e_esquecer_o_usuario():
    sessao = Sessao()
    usuario = usuario_com(Perfil.GESTOR)
    sessao.iniciar(usuario)
    assert sessao.usuario_atual is usuario
    sessao.encerrar()
    assert sessao.usuario_atual is None


# --- painel: C3, menu só com as opções do perfil ---------------------------

ROTULOS = {operacao: f"Fazer {operacao.name}" for operacao in Operacao}


@pytest.fixture
def painel_completo(sessao, controle_acesso):
    chamadas = []
    painel = PainelFronteira(sessao, controle_acesso)
    for operacao in Operacao:
        painel.registrar(AcaoDoPainel(
            operacao, ROTULOS[operacao],
            lambda operacao=operacao: chamadas.append(operacao)))
    painel.chamadas = chamadas
    return painel


@pytest.mark.parametrize("perfil", list(Perfil))
def test_c3_painel_deve_mostrar_so_as_opcoes_do_perfil(
        painel_completo, monkeypatch, capsys, perfil):
    monkeypatch.setattr("builtins.input", lambda _: "0")

    painel_completo.abrir(usuario_com(perfil))

    saida = capsys.readouterr().out
    for operacao in Operacao:
        assert (ROTULOS[operacao] in saida) is (operacao in ESPERADO[perfil])


def test_painel_deve_executar_a_acao_escolhida(
        painel_completo, monkeypatch):
    # Para o funcionário, a opção 1 é a primeira ação registrada que ele pode.
    respostas = iter(["1", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    painel_completo.abrir(usuario_com(Perfil.FUNCIONARIO))

    assert painel_completo.chamadas == [Operacao.REGISTRAR_EVIDENCIA]


@pytest.mark.parametrize("opcao", ["9", "-1", "abc", "", "٣"])
def test_painel_deve_recusar_opcao_fora_da_lista(
        painel_completo, monkeypatch, capsys, opcao):
    respostas = iter([opcao, "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    painel_completo.abrir(usuario_com(Perfil.FUNCIONARIO))

    assert "Opção inválida" in capsys.readouterr().out
    assert painel_completo.chamadas == []


def test_fiscal_so_deve_ver_a_opcao_de_sair(
        painel_completo, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    painel_completo.abrir(usuario_com(Perfil.FISCAL))
    saida = capsys.readouterr().out
    assert "PAINEL DO FISCAL" in saida
    assert "1 - " not in saida


def test_sessao_deve_valer_durante_o_painel_e_acabar_ao_sair(
        sessao, controle_acesso, monkeypatch):
    gestor = usuario_com(Perfil.GESTOR)
    vistos = []
    painel = PainelFronteira(sessao, controle_acesso)
    painel.registrar(AcaoDoPainel(
        Operacao.LISTAR_USUARIOS, "Listar",
        lambda: vistos.append(sessao.usuario_atual)))
    respostas = iter(["1", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    painel.abrir(gestor)

    assert vistos == [gestor]
    assert sessao.usuario_atual is None


def test_sessao_deve_acabar_mesmo_se_a_acao_falhar(
        sessao, controle_acesso, monkeypatch):
    painel = PainelFronteira(sessao, controle_acesso)

    def falha():
        raise RuntimeError("falhou")

    painel.registrar(AcaoDoPainel(Operacao.LISTAR_USUARIOS, "Listar", falha))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    with pytest.raises(RuntimeError):
        painel.abrir(usuario_com(Perfil.GESTOR))

    assert sessao.usuario_atual is None


# --- fronteira: listagem protegida e fluxo completo -------------------------

@pytest.fixture
def fronteira(controller, autenticacao, painel, sessao):
    fronteira = UsuarioFronteira(
        controller, AutenticacaoFronteira(
            autenticacao, painel, ler_senha=lambda _: "Senha@123"), sessao)
    painel.registrar(AcaoDoPainel(
        Operacao.LISTAR_USUARIOS, "Listar usuários",
        fronteira.listar_usuarios))
    return fronteira


def test_c2_listar_sem_login_deve_negar_e_nao_exibir_dados(
        fronteira, controller, dados_validos, capsys):
    controller.adicionar(dados_validos)

    fronteira.listar_usuarios()

    saida = capsys.readouterr().out
    assert "Acesso negado" in saida
    assert "maria@email.com" not in saida
    assert "Total" not in saida


def test_menu_principal_nao_deve_oferecer_a_listagem(
        fronteira, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    fronteira.menu()
    saida = capsys.readouterr().out
    assert "Listar usuários" not in saida
    assert "1 - Cadastrar usuário" in saida


def entrar_e_escolher(fronteira, monkeypatch, *entradas):
    fila = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _: next(fila))
    fronteira.menu()


def test_gestor_deve_listar_usuarios_pelo_painel(
        fronteira, controller, dados_validos, monkeypatch, capsys):
    controller.adicionar(dados_validos)  # maria é GESTOR
    # menu: 3 (entrar); login, perfil; painel: 1 (listar), 0 (sair); menu: 0
    entrar_e_escolher(fronteira, monkeypatch,
                      "3", "maria", "GESTOR", "1", "0", "0")

    saida = capsys.readouterr().out
    assert "1 - Listar usuários" in saida
    assert "maria@email.com" in saida
    assert "Acesso negado" not in saida


@pytest.mark.parametrize("perfil", ["FISCAL", "FUNCIONARIO"])
def test_outros_perfis_nao_veem_a_listagem_no_painel(
        fronteira, controller, dados_validos, monkeypatch, capsys, perfil):
    from dataclasses import replace
    controller.adicionar(replace(dados_validos, perfil=perfil))
    # painel: "1" não existe para esse perfil, depois "0"; menu: "0"
    entrar_e_escolher(fronteira, monkeypatch,
                      "3", "maria", perfil, "1", "0", "0")

    saida = capsys.readouterr().out
    assert "Listar usuários" not in saida
    assert "Opção inválida" in saida
    assert "maria@email.com" not in saida.split("PAINEL")[-1]
