from controle.validacao.validador import Validador
from excecao.validacao_error import TermosNaoAceitosError

RESPOSTAS_DE_ACEITE = ("s", "sim")


class ValidadorAceiteTermos(Validador):
    """Exige resposta afirmativa ("s" ou "sim") aos Termos de Uso."""

    def validar(self, valor: str) -> None:
        if valor.strip().lower() not in RESPOSTAS_DE_ACEITE:
            raise TermosNaoAceitosError()
