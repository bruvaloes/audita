from controle.comando.comando import Comando
from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.usuario_controller import UsuarioController
from entidade.usuario import Usuario


class CadastrarUsuarioComando(Comando[Usuario]):
    """Cadastra um novo usuário no sistema (RF 01)."""

    def __init__(self, usuarios: UsuarioController,
                 dados: DadosCadastroUsuario):
        self._usuarios = usuarios
        self._dados = dados

    def executar(self) -> Usuario:
        return self._usuarios.adicionar(self._dados)
