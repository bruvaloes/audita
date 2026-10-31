from enum import Enum


class SituacaoValidacao(Enum):
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    RECUSADA = "RECUSADA"

    @classmethod
    def de_texto(cls, texto: str) -> "SituacaoValidacao":
        """Converte o texto digitado (sem distinguir maiúsculas) em SituacaoValidacao.

        Levanta ValueError se o texto não corresponder a nenhuma situação.
        """
        return cls(texto.strip().upper())

    @classmethod
    def valores_validos(cls) -> str:
        return ", ".join(s.value for s in cls)
