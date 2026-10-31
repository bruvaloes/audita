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
from entidade.email import normalizar_email
from entidade.perfil import Perfil
from entidade.usuario import Usuario
from log.log_auditoria import LogAuditoria
from log.operacao_log import OperacaoLog
from log.registro_log import RegistroLog
from persistencia.usuario_repositorio import UsuarioRepositorio


class UsuarioController:

    def __init__(self, repositorio: UsuarioRepositorio,
                 validador: ValidadorCadastroUsuario,
                 hash_senha: HashSenha,
                 controle_acesso: ControleAcesso,
                 relogio: Callable[[], datetime] = datetime.now,
                 log: LogAuditoria | None = None):
        self._repositorio = repositorio
        self._validador = validador
        self._hash_senha = hash_senha
        self._controle_acesso = controle_acesso
        self._relogio = relogio
        self._log = log

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
        salvo = self._repositorio.salvar(usuario)
        if self._log:
            self._log.registrar(
                RegistroLog(
                    usuario=salvo.login,
                    operacao=OperacaoLog.CADASTRO,
                    data_hora=self._relogio(),
                    detalhes=f"Cadastro de usuario: {salvo.login} ({salvo.perfil.value})",
                )
            )
        return salvo

    def listar_todos(self, solicitante: Usuario | None) -> list[Usuario]:
        """Lista os usuários; levanta AcessoNegadoError se o solicitante
        não tiver permissão (RF 03)."""
        self._controle_acesso.verificar(solicitante, Operacao.LISTAR_USUARIOS)
        return self._repositorio.listar_todos()

    def contar(self) -> int:
        """Quantidade de usuários cadastrados (contagem agregada, sem dados
        pessoais)."""
        return len(self._repositorio.listar_todos())

    def _normalizar(self, dados: DadosCadastroUsuario) -> DadosCadastroUsuario:
        return DadosCadastroUsuario(
            nome=dados.nome,
            cpf=normalizar_cpf(dados.cpf),
            email=normalizar_email(dados.email),
            login=dados.login.strip(),
            senha=dados.senha,
            confirmacao_senha=dados.confirmacao_senha,
            perfil=dados.perfil,
            aceite_termos=dados.aceite_termos,
        )
