from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Resultado = TypeVar("Resultado")


class Comando(ABC, Generic[Resultado]):
    """Command (GoF): uma operação de negócio encapsulada em um objeto.

    Cada comando concreto guarda o receptor (o controller que sabe fazer a
    operação) e os dados do pedido, e só os usa quando `executar` é chamado.
    Assim, quem pede a operação (a fachada) não depende de como ela é feita.
    """

    @abstractmethod
    def executar(self) -> Resultado:
        """Executa a operação no receptor e devolve o resultado dela."""
