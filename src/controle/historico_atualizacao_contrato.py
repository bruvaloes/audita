from entidade.contrato_memento import ContratoMemento


class HistoricoAtualizacaoContrato:
    """Caretaker (GoF): guarda o memento da última atualização de contrato.

    Um único espaço: uma nova atualização substitui o anterior, e desfazer
    só limpa o espaço, sem guardar um novo memento (não há "refazer").
    """

    def __init__(self):
        self._entrada: tuple[str, ContratoMemento] | None = None

    def salvar(self, numero_atual: str, memento: ContratoMemento) -> None:
        self._entrada = (numero_atual, memento)

    def obter(self) -> tuple[str, ContratoMemento] | None:
        return self._entrada

    def limpar(self) -> None:
        self._entrada = None
