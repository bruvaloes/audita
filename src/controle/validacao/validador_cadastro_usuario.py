from operator import attrgetter

from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.validacao.validador import Validador
from controle.validacao.validador_campo_obrigatorio import (
    ValidadorCampoObrigatorio,
)
from controle.validacao.validador_cpf import ValidadorCpf
from controle.validacao.validador_email import ValidadorEmail
from controle.validacao.validador_login import ValidadorLogin
from controle.validacao.validador_perfil import ValidadorPerfil
from controle.validacao.validador_senha import ValidadorSenha
from controle.validacao.validador_unicidade import ValidadorUnicidade
from persistencia.usuario_repositorio import ConsultaUsuarios


class ValidadorCadastroUsuario:
    """Aplica, em ordem, as regras de cada campo do cadastro.

    Para criar uma nova regra basta implementar Validador e incluí-la em
    _regras; o controller não precisa mudar.
    """

    def __init__(self, consulta: ConsultaUsuarios):
        self._regras: list[tuple[str, Validador]] = [
            ("nome", ValidadorCampoObrigatorio("nome")),
            ("cpf", ValidadorCampoObrigatorio("cpf")),
            ("email", ValidadorCampoObrigatorio("e-mail")),
            ("senha", ValidadorCampoObrigatorio("senha")),
            ("perfil", ValidadorCampoObrigatorio("perfil")),
            ("login", ValidadorLogin()),
            ("senha", ValidadorSenha()),
            ("cpf", ValidadorCpf()),
            ("email", ValidadorEmail()),
            ("perfil", ValidadorPerfil()),
            ("cpf", ValidadorUnicidade.para_cpf(consulta)),
            ("email", ValidadorUnicidade.para_email(consulta)),
        ]

    def validar(self, dados: DadosCadastroUsuario) -> None:
        for campo, regra in self._regras:
            regra.validar(attrgetter(campo)(dados))
