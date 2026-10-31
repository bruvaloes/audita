from entidade.usuario import Usuario


class Sessao:
    """Guarda quem está autenticado enquanto o painel está aberto."""

    def __init__(self):
        self._usuario: Usuario | None = None

    @property
    def usuario_atual(self) -> Usuario | None:
        return self._usuario

    def iniciar(self, usuario: Usuario) -> None:
        self._usuario = usuario

    def encerrar(self) -> None:
        self._usuario = None
