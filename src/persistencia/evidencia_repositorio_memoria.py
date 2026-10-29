from entidade.evidencia import Evidencia
from entidade.situacao_validacao import SituacaoValidacao
from persistencia.evidencia_repositorio import EvidenciaRepositorio


class EvidenciaRepositorioMemoria(EvidenciaRepositorio):

    def __init__(self):
        self._evidencias: dict[int, Evidencia] = {}
        self._proximo_id: int = 1

    def salvar(self, evidencia: Evidencia) -> Evidencia:
        evidencia.id = self._proximo_id
        self._evidencias[evidencia.id] = evidencia
        self._proximo_id += 1
        return evidencia

    def buscar_por_id(self, id_evidencia: int) -> Evidencia | None:
        return self._evidencias.get(id_evidencia)

    def listar(
        self,
        numero_contrato: str | None = None,
        id_funcionario: int | None = None,
    ) -> list[Evidencia]:
        resultado = list(self._evidencias.values())
        if numero_contrato is not None:
            resultado = [e for e in resultado if e.numero_contrato == numero_contrato]
        if id_funcionario is not None:
            resultado = [e for e in resultado if e.id_funcionario == id_funcionario]
        return resultado

    def atualizar_situacao(
        self, id_evidencia: int, situacao: SituacaoValidacao
    ) -> None:
        if id_evidencia in self._evidencias:
            self._evidencias[id_evidencia].situacao = situacao
