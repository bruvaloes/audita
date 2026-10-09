from abc import ABC, abstractmethod


class Validador(ABC):
    """Regra de validação de um único valor.

    Levanta uma subclasse de ValidacaoError quando o valor é inválido.
    """

    @abstractmethod
    def validar(self, valor: str) -> None:
        ...
