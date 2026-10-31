from enum import Enum


class SituacaoContrato(Enum):
    ATIVO = "ATIVO"
    ENCERRADO = "ENCERRADO"

    @classmethod
    def de_texto(cls, texto: str) -> "SituacaoContrato":
        """Converte o texto digitado (sem distinguir maiúsculas) em SituacaoContrato.

        Levanta ValueError se o texto não corresponder a nenhuma situação.
        """
        return cls(texto.strip().upper())

    @classmethod
    def valores_validos(cls) -> str:
        return ", ".join(s.value for s in cls)
