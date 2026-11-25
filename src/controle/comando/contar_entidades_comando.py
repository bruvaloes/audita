from controle.comando.comando import Comando
from controle.contrato_controller import ContratoController
from controle.usuario_controller import UsuarioController
from negocio.evidencia_repositorio import EvidenciaRepositorio


class ContarEntidadesComando(Comando[dict[str, int]]):
    """Quantidade de cada tipo de entidade cadastrada e o total (RF 16).

    É uma contagem agregada, sem dados pessoais, e por isso não exige login.
    Sem repositório de evidências, as evidências contam zero.
    """

    def __init__(self, usuarios: UsuarioController,
                 contratos: ContratoController,
                 evidencias: EvidenciaRepositorio | None):
        self._usuarios = usuarios
        self._contratos = contratos
        self._evidencias = evidencias

    def executar(self) -> dict[str, int]:
        usuarios = self._usuarios.contar()
        contratos = self._contratos.contar()
        evidencias = (len(self._evidencias.listar())
                      if self._evidencias is not None else 0)
        return {
            "usuarios": usuarios,
            "contratos": contratos,
            "evidencias": evidencias,
            "total": usuarios + contratos + evidencias,
        }
