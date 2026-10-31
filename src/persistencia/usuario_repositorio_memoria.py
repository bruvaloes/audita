from entidade.usuario import Usuario
from excecao.persistencia_error import EscritaPersistenciaError
from persistencia.usuario_repositorio import UsuarioRepositorio


class UsuarioRepositorioMemoria(UsuarioRepositorio):

    def __init__(self):
        self._usuarios: dict[int, Usuario] = {}
        self._proximo_id: int = 1

    def salvar(self, usuario: Usuario) -> Usuario:
        self._recusar_duplicado(usuario)
        usuario.id = self._proximo_id
        self._usuarios[usuario.id] = usuario
        self._proximo_id += 1
        return usuario

    def listar_todos(self) -> list[Usuario]:
        return list(self._usuarios.values())

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        return self._buscar(lambda usuario: usuario.cpf == cpf)

    def buscar_por_login(self, login: str) -> Usuario | None:
        return self._buscar(
            lambda usuario: usuario.login.casefold() == login.casefold())

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self._buscar(lambda usuario: usuario.email == email)

    def _recusar_duplicado(self, usuario: Usuario) -> None:
        """Mesma garantia do UNIQUE do SQLite em CPF, e-mail e login."""
        if self.buscar_por_cpf(usuario.cpf):
            campo = "CPF"
        elif self.buscar_por_email(usuario.email):
            campo = "e-mail"
        elif self.buscar_por_login(usuario.login):
            campo = "login"
        else:
            return
        raise EscritaPersistenciaError(
            f"Erro ao salvar usuário: {campo} já cadastrado")

    def _buscar(self, criterio) -> Usuario | None:
        return next(
            (usuario for usuario in self._usuarios.values()
             if criterio(usuario)),
            None,
        )
