"""RF02: autenticação por login, CPF ou e-mail, com senha e perfil (RN02.1 a
RN02.3 e RN02.6), e o registro de cada tentativa como Acesso."""
import pytest

from controle.autenticacao_controller import AutenticacaoController
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from entidade.usuario import Usuario
from excecao.credenciais_invalidas_error import CredenciaisInvalidasError
from excecao.persistencia_error import EscritaPersistenciaError
from fronteira.autenticacao_fronteira import AutenticacaoFronteira
from fronteira.painel_fronteira import PainelFronteira
from fronteira.usuario_fronteira import UsuarioFronteira
from persistencia.acesso_repositorio import AcessoRepositorio

SENHA = "Senha@123"
CPF_MARIA = "52998224725"
EMAIL_MARIA = "maria@email.com"
CPF_JOAO = "11144477735"


@pytest.fixture
def maria(repositorio, hash_senha):
    """Usuária ATIVA com perfil GESTOR."""
    return repositorio.salvar(Usuario(
        0, "Maria", CPF_MARIA, EMAIL_MARIA, "maria",
        hash_senha.gerar(SENHA), Perfil.GESTOR))


@pytest.fixture
def joao_inativo(repositorio, hash_senha):
    """Usuário INATIVO com perfil FISCAL."""
    return repositorio.salvar(Usuario(
        0, "João", CPF_JOAO, "joao@email.com", "joao",
        hash_senha.gerar(SENHA), Perfil.FISCAL, ativo=False))


def test_c1_deve_autenticar_por_login_senha_e_perfil_corretos(
        autenticacao, maria):
    assert autenticacao.autenticar("maria", SENHA, "GESTOR") == maria


def test_c2_deve_autenticar_por_cpf_com_a_senha_correta(autenticacao, maria):
    assert autenticacao.autenticar(CPF_MARIA, SENHA, "GESTOR") == maria


def test_c2_deve_autenticar_por_email_com_a_senha_correta(
        autenticacao, maria):
    assert autenticacao.autenticar(EMAIL_MARIA, SENHA, "GESTOR") == maria


def test_deve_ignorar_maiusculas_no_perfil_e_espacos_no_identificador(
        autenticacao, maria):
    assert autenticacao.autenticar("  maria  ", SENHA, "gestor") == maria


def test_c3_deve_recusar_senha_incorreta(autenticacao, maria):
    with pytest.raises(CredenciaisInvalidasError) as erro:
        autenticacao.autenticar("maria", "Outra@123", "GESTOR")
    assert str(erro.value) == "Credenciais inválidas"


def test_c4_deve_recusar_perfil_divergente_com_senha_correta(
        autenticacao, maria):
    with pytest.raises(CredenciaisInvalidasError) as erro:
        autenticacao.autenticar("maria", SENHA, "FISCAL")
    assert str(erro.value) == "Credenciais inválidas"


def test_rn02_6_deve_recusar_usuario_inativo(autenticacao, joao_inativo):
    with pytest.raises(CredenciaisInvalidasError) as erro:
        autenticacao.autenticar("joao", SENHA, "FISCAL")
    assert str(erro.value) == "Credenciais inválidas"


def test_deve_recusar_usuario_inexistente(autenticacao, maria):
    with pytest.raises(CredenciaisInvalidasError):
        autenticacao.autenticar("carlos", SENHA, "GESTOR")


def test_deve_recusar_perfil_que_nao_existe(autenticacao, maria):
    with pytest.raises(CredenciaisInvalidasError):
        autenticacao.autenticar("maria", SENHA, "DIRETOR")


@pytest.mark.parametrize("identificador, senha, perfil", [
    ("", SENHA, "GESTOR"),
    ("maria", "", "GESTOR"),
    ("maria", SENHA, ""),
])
def test_deve_recusar_campo_vazio(
        autenticacao, maria, identificador, senha, perfil):
    with pytest.raises(CredenciaisInvalidasError):
        autenticacao.autenticar(identificador, senha, perfil)


@pytest.mark.parametrize("login", ["MARIA", "Maria", "  maria  "])
def test_login_pelo_apelido_ignora_maiusculas(autenticacao, maria, login):
    assert autenticacao.autenticar(login, SENHA, "GESTOR") == maria


def test_c2_deve_autenticar_por_cpf_com_pontuacao(autenticacao, maria):
    assert autenticacao.autenticar("529.982.247-25", SENHA, "GESTOR") == maria


def test_cpf_com_pontuacao_e_senha_incorreta_deve_ser_recusado(
        autenticacao, maria):
    with pytest.raises(CredenciaisInvalidasError) as erro:
        autenticacao.autenticar("529.982.247-25", "Outra@123", "GESTOR")
    assert str(erro.value) == "Credenciais inválidas"


@pytest.mark.parametrize("identificador", ["...-", "-", ".", ".-.-."])
def test_identificador_so_com_pontuacao_nao_identifica_ninguem(
        autenticacao, maria, identificador):
    with pytest.raises(CredenciaisInvalidasError):
        autenticacao.autenticar(identificador, SENHA, "GESTOR")


@pytest.mark.parametrize("identificador", [
    "Maria@Email.com", "MARIA@EMAIL.COM", "  maria@email.com  "])
def test_login_por_email_ignora_maiusculas(
        autenticacao, maria, identificador):
    assert autenticacao.autenticar(identificador, SENHA, "GESTOR") == maria


@pytest.mark.parametrize("identificador, senha, perfil", [
    ("maria", "Outra@123", "GESTOR"),
    ("maria", SENHA, "FISCAL"),
    ("joao", SENHA, "FISCAL"),
    ("carlos", SENHA, "GESTOR"),
    ("maria", SENHA, "DIRETOR"),
])
def test_rn02_3_toda_falha_deve_ter_a_mesma_mensagem(
        autenticacao, maria, joao_inativo, identificador, senha, perfil):
    with pytest.raises(CredenciaisInvalidasError) as erro:
        autenticacao.autenticar(identificador, senha, perfil)
    assert str(erro.value) == "Credenciais inválidas"


@pytest.mark.parametrize(
    "identificador, senha, perfil, login_esperado, perfil_esperado, resultado",
    [
        ("maria", SENHA, "GESTOR", "maria", Perfil.GESTOR,
         ResultadoAcesso.SUCESSO),
        (CPF_MARIA, SENHA, "GESTOR", "maria", Perfil.GESTOR,
         ResultadoAcesso.SUCESSO),
        (EMAIL_MARIA, SENHA, "GESTOR", "maria", Perfil.GESTOR,
         ResultadoAcesso.SUCESSO),
        ("maria", "Outra@123", "GESTOR", "maria", Perfil.GESTOR,
         ResultadoAcesso.CREDENCIAIS_INVALIDAS),
        ("maria", SENHA, "FISCAL", "maria", Perfil.FISCAL,
         ResultadoAcesso.CREDENCIAIS_INVALIDAS),
        ("joao", SENHA, "FISCAL", "joao", Perfil.FISCAL,
         ResultadoAcesso.CREDENCIAIS_INVALIDAS),
        ("carlos", SENHA, "GESTOR", None, Perfil.GESTOR,
         ResultadoAcesso.CREDENCIAIS_INVALIDAS),
        ("maria", SENHA, "DIRETOR", "maria", None,
         ResultadoAcesso.CREDENCIAIS_INVALIDAS),
    ])
def test_tentativa_gera_um_acesso(
        autenticacao, acessos, repositorio, maria, joao_inativo,
        identificador, senha, perfil, login_esperado, perfil_esperado,
        resultado):
    try:
        autenticacao.autenticar(identificador, senha, perfil)
    except CredenciaisInvalidasError:
        pass

    usuario = (repositorio.buscar_por_login(login_esperado)
               if login_esperado else None)
    (acesso,) = acessos.listar_todos()
    assert (acesso.usuario_id, acesso.perfil, acesso.resultado) == (
        usuario.id if usuario else None, perfil_esperado, resultado)


def test_cada_tentativa_deve_gerar_um_acesso_novo(
        autenticacao, acessos, maria):
    autenticacao.autenticar("maria", SENHA, "GESTOR")
    with pytest.raises(CredenciaisInvalidasError):
        autenticacao.autenticar("maria", "Outra@123", "GESTOR")
    autenticacao.autenticar("maria", SENHA, "GESTOR")

    assert [acesso.resultado for acesso in acessos.listar_todos()] == [
        ResultadoAcesso.SUCESSO,
        ResultadoAcesso.CREDENCIAIS_INVALIDAS,
        ResultadoAcesso.SUCESSO,
    ]


def test_acesso_deve_registrar_a_data_e_hora_da_tentativa(
        autenticacao, acessos, maria, momento):
    autenticacao.autenticar("maria", SENHA, "GESTOR")

    assert acessos.listar_todos()[0].data_hora == momento


class AcessosComFalhaNaEscrita(AcessoRepositorio):
    def salvar(self, acesso):
        raise EscritaPersistenciaError("disco cheio")

    def listar_todos(self):
        return []


def test_nao_deve_conceder_login_quando_o_registro_do_acesso_falha(
        repositorio, hash_senha, maria):
    autenticacao = AutenticacaoController(
        repositorio, AcessosComFalhaNaEscrita(), hash_senha)

    with pytest.raises(EscritaPersistenciaError):
        autenticacao.autenticar("maria", SENHA, "GESTOR")


# --- Fronteira: opção de login no menu e painel após a autenticação ---

def abrir_menu_e_entrar(controller, autenticacao, painel, sessao,
                        monkeypatch, senha, *entradas):
    """Escolhe a opção 3 do menu e responde ao login; `entradas` vêm depois
    do menu (identificador, perfil e o que mais a tela pedir)."""
    fila = iter(("3", *entradas))
    monkeypatch.setattr("builtins.input", lambda _: next(fila))
    fronteira = UsuarioFronteira(controller, AutenticacaoFronteira(
        autenticacao, painel, ler_senha=lambda _: senha), sessao)
    fronteira.menu()


def test_menu_deve_oferecer_a_opcao_de_login(
        controller, autenticacao, painel, sessao, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    UsuarioFronteira(controller, AutenticacaoFronteira(
        autenticacao, painel), sessao).menu()

    assert "3 - Entrar (login)" in capsys.readouterr().out


def test_c1_deve_abrir_o_painel_do_gestor_apos_autenticar(
        controller, autenticacao, maria, painel, sessao, monkeypatch, capsys):
    # login, perfil, "0" (sair do painel) e "0" (sair do menu)
    abrir_menu_e_entrar(controller, autenticacao, painel, sessao,
                        monkeypatch, SENHA,
                        "maria", "GESTOR", "0", "0")

    saida = capsys.readouterr().out
    assert "PAINEL DO GESTOR" in saida
    assert "Credenciais inválidas" not in saida


def test_c3_tela_deve_mostrar_credenciais_invalidas_e_nao_abrir_painel(
        controller, autenticacao, maria, painel, sessao, monkeypatch, capsys):
    abrir_menu_e_entrar(controller, autenticacao, painel, sessao,
                        monkeypatch, "Outra@123",
                        "maria", "GESTOR", "0")

    saida = capsys.readouterr().out
    assert "Credenciais inválidas" in saida
    assert "PAINEL" not in saida


def test_tela_deve_informar_erro_de_armazenamento_sem_abrir_painel(
        controller, repositorio, hash_senha, maria, painel, sessao, monkeypatch, capsys):
    autenticacao = AutenticacaoController(
        repositorio, AcessosComFalhaNaEscrita(), hash_senha)

    abrir_menu_e_entrar(controller, autenticacao, painel, sessao,
                        monkeypatch, SENHA,
                        "maria", "GESTOR", "0")

    saida = capsys.readouterr().out
    assert "Erro de armazenamento: disco cheio" in saida
    assert "PAINEL" not in saida


@pytest.mark.parametrize("perfil, titulo", [
    (Perfil.GESTOR, "PAINEL DO GESTOR"),
    (Perfil.FISCAL, "PAINEL DO FISCAL"),
    (Perfil.FUNCIONARIO, "PAINEL DO FUNCIONÁRIO"),
])
def test_painel_deve_ser_o_do_perfil_do_usuario(
        painel, monkeypatch, capsys, perfil, titulo):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    usuario = Usuario(1, "Ana", CPF_MARIA, EMAIL_MARIA, "ana", "hash", perfil)

    painel.abrir(usuario)

    assert titulo in capsys.readouterr().out
