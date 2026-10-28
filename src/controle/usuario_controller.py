from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.seguranca.hash_senha import HashSenha
from controle.validacao.validador_cadastro_usuario import (
    ValidadorCadastroUsuario,
)
from entidade.cpf import normalizar_cpf
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from persistencia.usuario_repositorio import UsuarioRepositorio


class UsuarioController:

    def __init__(self, repositorio: UsuarioRepositorio,
                 validador: ValidadorCadastroUsuario,
                 hash_senha: HashSenha):
        self._repositorio = repositorio
        self._validador = validador
        self._hash_senha = hash_senha

    def adicionar(self, dados: DadosCadastroUsuario) -> Usuario:
        dados = self._normalizar(dados)
        self._validador.validar(dados)

        usuario = Usuario(
            id=0,
            nome=dados.nome,
            cpf=dados.cpf,
            email=dados.email,
            login=dados.login,
            senha_hash=self._hash_senha.gerar(dados.senha),
            perfil=Perfil.de_texto(dados.perfil),
        )
        return self._repositorio.salvar(usuario)

    def listar_todos(self) -> list[Usuario]:
        return self._repositorio.listar_todos()

    def _normalizar(self, dados: DadosCadastroUsuario) -> DadosCadastroUsuario:
        return DadosCadastroUsuario(
            nome=dados.nome,
            cpf=normalizar_cpf(dados.cpf),
            email=dados.email,
            login=dados.login.strip(),
            senha=dados.senha,
            confirmacao_senha=dados.confirmacao_senha,
            perfil=dados.perfil,
        )
