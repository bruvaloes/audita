"""RF02: autenticação por login, CPF ou e-mail, com senha e perfil (RN02.1 a
RN02.3 e RN02.6), e o registro de cada tentativa como Acesso."""
import pytest

from controle.autenticacao_controller import AutenticacaoController
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from entidade.usuario import Usuario
from excecao.credenciais_invalidas_error import CredenciaisInvalidasError
from excecao.persistencia_error import EscritaPersistenciaError
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


def test_cpf_so_identifica_quando_digitado_apenas_com_numeros(
        autenticacao, maria):
    with pytest.raises(CredenciaisInvalidasError):
        autenticacao.autenticar("529.982.247-25", SENHA, "GESTOR")


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

    usuario = repositorio.buscar_por_login(login_esperado)
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
