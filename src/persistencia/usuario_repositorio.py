from entidade.usuario import Usuario


class UsuarioRepositorio:

    def __init__(self):
        self._usuarios: dict[int, Usuario] = {}
        self._proximo_id: int = 1

    def salvar(self, usuario: Usuario) -> Usuario:
        usuario.id = self._proximo_id
        self._usuarios[usuario.id] = usuario
        self._proximo_id += 1
        return usuario
