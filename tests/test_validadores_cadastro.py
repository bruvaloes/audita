"""Testes unitários dos validadores do cadastro, isolados do controller."""
import pytest

from controle.validacao.validador_campo_obrigatorio import (
    ValidadorCampoObrigatorio,
)
from controle.validacao.validador_email import ValidadorEmail
from controle.validacao.validador_login import ValidadorLogin
from controle.validacao.validador_nome import ValidadorNome
from controle.validacao.validador_perfil import ValidadorPerfil
from controle.validacao.validador_unicidade import ValidadorUnicidade
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from excecao.login_invalido_error import (
    LoginComNumerosError,
    LoginMuitoLongoError,
    LoginVazioError,
)
from excecao.validacao_error import (
    CampoObrigatorioError,
    EmailInvalidoError,
    NomeMuitoLongoError,
    PerfilInvalidoError,
    UsuarioDuplicadoError,
)
from persistencia.usuario_repositorio_memoria import UsuarioRepositorioMemoria


class TestCampoObrigatorio:

    @pytest.mark.parametrize("valor", ["", "   ", "\t"])
    def test_deve_rejeitar_vazio_ou_so_espacos(self, valor):
        with pytest.raises(CampoObrigatorioError):
            ValidadorCampoObrigatorio("nome").validar(valor)

    def test_deve_citar_o_campo_na_mensagem(self):
        with pytest.raises(CampoObrigatorioError, match="'e-mail'"):
            ValidadorCampoObrigatorio("e-mail").validar("")

    def test_deve_aceitar_texto(self):
        ValidadorCampoObrigatorio("nome").validar("Maria")


class TestNome:

    def test_deve_aceitar_nome_no_limite(self):
        ValidadorNome().validar("a" * 100)

    def test_deve_rejeitar_nome_acima_do_limite(self):
        with pytest.raises(NomeMuitoLongoError):
            ValidadorNome().validar("a" * 101)


class TestEmail:

    @pytest.mark.parametrize("email", [
        "maria@email.com", "a@b", "maria.silva+x@dominio.com.br",
        "a" * 90 + "@email.com",
    ])
    def test_deve_aceitar_formato_nome_arroba_dominio(self, email):
        ValidadorEmail().validar(email)

    @pytest.mark.parametrize("email", [
        "", "maria", "maria@", "@email.com", "a@@b.com", "a@b@c.com",
        "ma ria@email.com", "maria@ email.com", "a" * 91 + "@email.com",
    ])
    def test_deve_rejeitar_formato_invalido_ou_acima_de_100(self, email):
        with pytest.raises(EmailInvalidoError):
            ValidadorEmail().validar(email)


class TestLogin:

    @pytest.mark.parametrize("login", ["maria", "a", "a" * 12, "Ana_Souza"])
    def test_deve_aceitar_login_valido(self, login):
        ValidadorLogin().validar(login)

    @pytest.mark.parametrize("login", ["", "   "])
    def test_deve_rejeitar_login_vazio(self, login):
        with pytest.raises(LoginVazioError):
            ValidadorLogin().validar(login)

    def test_deve_rejeitar_login_acima_de_12_caracteres(self):
        with pytest.raises(LoginMuitoLongoError):
            ValidadorLogin().validar("a" * 13)

    @pytest.mark.parametrize("login", ["ana2", "1ana", "a1b"])
    def test_deve_rejeitar_login_com_numero(self, login):
        with pytest.raises(LoginComNumerosError):
            ValidadorLogin().validar(login)


class TestPerfil:

    @pytest.mark.parametrize("perfil", ["GESTOR", "fiscal", " Funcionario "])
    def test_deve_aceitar_perfil_do_enum(self, perfil):
        ValidadorPerfil().validar(perfil)

    def test_deve_rejeitar_perfil_desconhecido(self):
        with pytest.raises(PerfilInvalidoError):
            ValidadorPerfil().validar("ADMIN")


class TestUnicidade:

    @pytest.fixture
    def repositorio(self):
        repositorio = UsuarioRepositorioMemoria()
        repositorio.salvar(Usuario(
            0, "Maria", "52998224725", "maria@email.com", "maria", "hash",
            Perfil.GESTOR))
        return repositorio

    @pytest.mark.parametrize("fabrica, valor, mensagem", [
        (ValidadorUnicidade.para_cpf, "52998224725", "CPF já cadastrado"),
        (ValidadorUnicidade.para_email, "maria@email.com",
         "E-mail já cadastrado"),
        (ValidadorUnicidade.para_login, "maria", "Login já cadastrado"),
    ])
    def test_deve_rejeitar_valor_ja_cadastrado(
            self, repositorio, fabrica, valor, mensagem):
        with pytest.raises(UsuarioDuplicadoError) as erro:
            fabrica(repositorio).validar(valor)
        assert str(erro.value) == mensagem

    @pytest.mark.parametrize("fabrica, valor", [
        (ValidadorUnicidade.para_cpf, "11144477735"),
        (ValidadorUnicidade.para_email, "joao@email.com"),
        (ValidadorUnicidade.para_login, "joao"),
    ])
    def test_deve_aceitar_valor_novo(self, repositorio, fabrica, valor):
        fabrica(repositorio).validar(valor)
