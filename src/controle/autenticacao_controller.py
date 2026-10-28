from datetime import datetime
from typing import Callable

from controle.seguranca.hash_senha import HashSenha
from controle.validacao.validador_email import SEPARADOR_EMAIL
from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from entidade.usuario import Usuario
from excecao.credenciais_invalidas_error import CredenciaisInvalidasError
from persistencia.acesso_repositorio import PersistenciaAcessos
from persistencia.usuario_repositorio import ConsultaUsuarios

# Senha sem valor: só dá trabalho ao verificador quando o usuário não existe.
SENHA_FICTICIA = "senha-ficticia-sem-usuario"


class AutenticacaoController:
    """Autentica um usuário e registra cada tentativa como um Acesso."""

    def __init__(self, consulta_usuarios: ConsultaUsuarios,
                 acessos: PersistenciaAcessos,
                 hash_senha: HashSenha,
                 relogio: Callable[[], datetime] = datetime.now):
        self._consulta_usuarios = consulta_usuarios
        self._acessos = acessos
        self._hash_senha = hash_senha
        self._relogio = relogio
        self._hash_ficticio = hash_senha.gerar(SENHA_FICTICIA)

    def autenticar(self, identificador: str, senha: str,
                   perfil: str) -> Usuario:
        """Retorna o usuário autenticado ou levanta CredenciaisInvalidasError.

        `identificador` é o login, o CPF (só números) ou o e-mail (RN02.1).
        Toda tentativa gera exatamente um Acesso; se o registro falhar, a
        PersistenciaError sobe e o login não é concedido.
        """
        usuario = self._localizar(identificador.strip())
        perfil_informado = self._ler_perfil(perfil)
        # A senha é sempre verificada, para a falha não ser mais rápida
        # quando o usuário não existe.
        senha_confere = self._senha_confere(usuario, senha)

        autenticou = (
            usuario is not None
            and senha_confere
            and usuario.ativo
            and usuario.perfil == perfil_informado
        )
        resultado = (ResultadoAcesso.SUCESSO if autenticou
                     else ResultadoAcesso.CREDENCIAIS_INVALIDAS)
        self._registrar(usuario, perfil_informado, resultado)

        if not autenticou:
            raise CredenciaisInvalidasError()
        return usuario

    def _localizar(self, identificador: str) -> Usuario | None:
        if SEPARADOR_EMAIL in identificador:
            return self._consulta_usuarios.buscar_por_email(identificador)
        if identificador.isascii() and identificador.isdigit():
            return self._consulta_usuarios.buscar_por_cpf(identificador)
        return self._consulta_usuarios.buscar_por_login(identificador)

    @staticmethod
    def _ler_perfil(texto: str) -> Perfil | None:
        try:
            return Perfil.de_texto(texto)
        except ValueError:
            return None

    def _senha_confere(self, usuario: Usuario | None, senha: str) -> bool:
        hash_conferido = usuario.senha_hash if usuario else self._hash_ficticio
        return self._hash_senha.verificar(senha, hash_conferido)

    def _registrar(self, usuario: Usuario | None, perfil: Perfil | None,
                   resultado: ResultadoAcesso) -> None:
        self._acessos.salvar(Acesso(
            id=0,
            usuario_id=usuario.id if usuario else None,
            perfil=perfil,
            data_hora=self._relogio(),
            resultado=resultado,
        ))
