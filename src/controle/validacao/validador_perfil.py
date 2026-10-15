from controle.validacao.validador import Validador
from entidade.perfil import Perfil
from excecao.validacao_error import PerfilInvalidoError


class ValidadorPerfil(Validador):

    def validar(self, valor: str) -> None:
        try:
            Perfil.de_texto(valor)
        except ValueError:
            raise PerfilInvalidoError(valor, Perfil.nomes_validos())
