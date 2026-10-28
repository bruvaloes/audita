from controle.validacao.validador import Validador
from excecao.validacao_error import EmailInvalidoError

SEPARADOR_EMAIL = "@"
TAMANHO_MAXIMO_EMAIL = 100


class ValidadorEmail(Validador):
    """Aceita o formato nome@dominio, sem espaços, com até 100 caracteres."""

    def validar(self, valor: str) -> None:
        if not self._formato_valido(valor) or len(valor) > TAMANHO_MAXIMO_EMAIL:
            raise EmailInvalidoError(TAMANHO_MAXIMO_EMAIL)

    @staticmethod
    def _formato_valido(valor: str) -> bool:
        nome, separador, dominio = valor.partition(SEPARADOR_EMAIL)
        return bool(
            separador and nome and dominio
            and SEPARADOR_EMAIL not in dominio
            and not any(caractere.isspace() for caractere in valor)
        )
