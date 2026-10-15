from entidade.usuario import Usuario
from persistencia.usuario_repositorio import UsuarioRepositorio


class UsuarioRepositorioMemoria(UsuarioRepositorio):

    def __init__(self):
        self._usuarios: dict[int, Usuario] = {}
        self._proximo_id: int = 1

    def salvar(self, usuario: Usuario) -> Usuario:
        usuario.id = self._proximo_id
        self._usuarios[usuario.id] = usuario
        self._proximo_id += 1
        return usuario

    def listar_todos(self) -> list[Usuario]:
        return list(self._usuarios.values())

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        return self._buscar(lambda usuario: usuario.cpf == cpf)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self._buscar(lambda usuario: usuario.email == email)

    def _buscar(self, criterio) -> Usuario | None:
        return next(
            (usuario for usuario in self._usuarios.values()
             if criterio(usuario)),
            None,
        )
