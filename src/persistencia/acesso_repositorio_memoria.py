from entidade.acesso import Acesso
from persistencia.acesso_repositorio import AcessoRepositorio


class AcessoRepositorioMemoria(AcessoRepositorio):

    def __init__(self):
        self._acessos: list[Acesso] = []

    def salvar(self, acesso: Acesso) -> Acesso:
        acesso.id = len(self._acessos) + 1
        self._acessos.append(acesso)
        return acesso

    def listar_todos(self) -> list[Acesso]:
        return list(self._acessos)
