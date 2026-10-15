from enum import Enum


class Perfil(Enum):
    GESTOR = "GESTOR"
    FISCAL = "FISCAL"
    FUNCIONARIO = "FUNCIONARIO"

    @classmethod
    def de_texto(cls, texto: str) -> "Perfil":
        """Converte o texto digitado (sem distinguir maiúsculas) em Perfil.

        Levanta ValueError se o texto não corresponder a nenhum perfil.
        """
        return cls(texto.strip().upper())

    @classmethod
    def nomes_validos(cls) -> str:
        return ", ".join(perfil.value for perfil in cls)
