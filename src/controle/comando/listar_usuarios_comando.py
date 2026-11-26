from controle.comando.comando import Comando
from controle.usuario_controller import UsuarioController
from entidade.usuario import Usuario


class ListarUsuariosComando(Comando[list[Usuario]]):
    """Lista os usuários cadastrados para quem tem permissão (RF 01)."""

    def __init__(self, usuarios: UsuarioController,
                 solicitante: Usuario | None):
        self._usuarios = usuarios
        self._solicitante = solicitante

    def executar(self) -> list[Usuario]:
        return self._usuarios.listar_todos(self._solicitante)
