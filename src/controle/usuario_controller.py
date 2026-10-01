from entidade.perfil import Perfil
from excecao.login_invalido_error import (
    LoginComNumerosError,
    LoginMuitoLongoError,
    LoginVazioError,
)
from entidade.usuario import Usuario
from persistencia.usuario_repositorio import UsuarioRepositorio


TAMANHO_MAXIMO_LOGIN = 12


class UsuarioController:

    def __init__(self, repositorio: UsuarioRepositorio):
        self._repositorio = repositorio

    def adicionar(self, nome: str, cpf: str, email: str, login: str,
                  senha: str, perfil_str: str) -> Usuario:
        self._validar_campos_obrigatorios(nome, cpf, email, senha, perfil_str)
        self._validar_login(login)
        self._validar_cpf(cpf)
        self._validar_email(email)
        self._validar_unicidade_cpf(cpf)
        self._validar_unicidade_email(email)
        perfil = self._converter_perfil(perfil_str)

        usuario = Usuario(
            id=0,
            nome=nome,
            cpf=cpf,
            email=email,
            login=login,
            senha=senha,
            perfil=perfil,
        )
        return self._repositorio.salvar(usuario)

    def listar_todos(self) -> list[Usuario]:
        return self._repositorio.listar_todos()

    def _validar_campos_obrigatorios(self, nome: str, cpf: str, email: str,
                                     senha: str, perfil_str: str) -> None:
        if not all([nome.strip(), cpf.strip(), email.strip(),
                    senha.strip(), perfil_str.strip()]):
            raise ValueError("Todos os campos são obrigatórios.")

    def _validar_login(self, login: str) -> None:
        if not login.strip():
            raise LoginVazioError()
        if len(login) > TAMANHO_MAXIMO_LOGIN:
            raise LoginMuitoLongoError(TAMANHO_MAXIMO_LOGIN)
        if any(caractere.isdigit() for caractere in login):
            raise LoginComNumerosError()

    def _validar_cpf(self, cpf: str) -> None:
        digitos = cpf.replace(".", "").replace("-", "")
        if not digitos.isdigit() or len(digitos) != 11:
            raise ValueError("CPF deve conter exatamente 11 dígitos numéricos.")

    def _validar_email(self, email: str) -> None:
        if "@" not in email:
            raise ValueError("E-mail deve conter '@'.")

    def _validar_unicidade_cpf(self, cpf: str) -> None:
        if self._repositorio.buscar_por_cpf(cpf):
            raise ValueError("Já existe um usuário com este CPF.")

    def _validar_unicidade_email(self, email: str) -> None:
        if self._repositorio.buscar_por_email(email):
            raise ValueError("Já existe um usuário com este e-mail.")

    def _converter_perfil(self, perfil_str: str) -> Perfil:
        try:
            return Perfil(perfil_str.strip().upper())
        except ValueError:
            nomes_validos = ", ".join(p.value for p in Perfil)
            raise ValueError(
                f"Perfil inválido: '{perfil_str}'. "
                f"Valores aceitos: {nomes_validos}."
            )
