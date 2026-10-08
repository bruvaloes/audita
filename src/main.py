from persistencia.usuario_repositorio import UsuarioRepositorioMemoria
from controle.usuario_controller import UsuarioController
from fronteira.usuario_fronteira import UsuarioFronteira


def main():
    repositorio = UsuarioRepositorioMemoria()
    controller = UsuarioController(repositorio)
    fronteira = UsuarioFronteira(controller)
    fronteira.menu()


if __name__ == "__main__":
    main()
