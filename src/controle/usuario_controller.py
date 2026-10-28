from datetime import datetime
from typing import Callable

from controle.acesso.controle_acesso import ControleAcesso
from controle.acesso.operacao import Operacao
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
                 hash_senha: HashSenha,
                 controle_acesso: ControleAcesso,
                 relogio: Callable[[], datetime] = datetime.now):
        self._repositorio = repositorio
        self._validador = validador
        self._hash_senha = hash_senha
        self._controle_acesso = controle_acesso
        self._relogio = relogio

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
            aceite_termos_em=self._relogio(),
        )
        return self._repositorio.salvar(usuario)

    def listar_todos(self, solicitante: Usuario | None) -> list[Usuario]:
        """Lista os usuários; levanta AcessoNegadoError se o solicitante
        não tiver permissão (RF 03)."""
        self._controle_acesso.verificar(solicitante, Operacao.LISTAR_USUARIOS)
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
            aceite_termos=dados.aceite_termos,
        )
