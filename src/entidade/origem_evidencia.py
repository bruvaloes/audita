from enum import Enum


class OrigemEvidencia(Enum):
    CAMERA = "CAMERA"
    GALERIA = "GALERIA"

    @classmethod
    def de_texto(cls, texto: str) -> "OrigemEvidencia":
        """Converte o texto digitado (sem distinguir maiúsculas) em OrigemEvidencia.

        Levanta ValueError se o texto não corresponder a nenhuma origem.
        """
        return cls(texto.strip().upper())

    @classmethod
    def valores_validos(cls) -> str:
        return ", ".join(o.value for o in cls)
