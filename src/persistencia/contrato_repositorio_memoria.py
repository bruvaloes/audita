from entidade.contrato import Contrato
from persistencia.contrato_repositorio import ContratoRepositorio


class ContratoRepositorioMemoria(ContratoRepositorio):

    def __init__(self):
        self._contratos: dict[str, Contrato] = {}
        self._proximo_id: int = 1

    def salvar(self, contrato: Contrato) -> Contrato:
        contrato.id = self._proximo_id
        self._contratos[contrato.numero] = contrato
        self._proximo_id += 1
        return contrato

    def listar(self) -> list[Contrato]:
        return list(self._contratos.values())

    def buscar_por_numero(self, numero: str) -> Contrato | None:
        return self._contratos.get(numero)

    def atualizar(self, contrato: Contrato) -> None:
        self._contratos[contrato.numero] = contrato

    def remover(self, numero: str) -> None:
        self._contratos.pop(numero, None)
