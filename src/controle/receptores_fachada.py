from dataclasses import dataclass

from controle.autenticacao_controller import AutenticacaoController
from controle.contrato_controller import ContratoController
from controle.relatorio_controller import RelatorioController
from controle.usuario_controller import UsuarioController
from negocio.evidencia_repositorio import EvidenciaRepositorio


@dataclass(frozen=True)
class ReceptoresFachada:
    """Receptores dos comandos montados pela fachada (Issue #25).

    Agrupa os controllers e o repositório de evidências que a fachada entrega
    aos comandos, para que ela não receba mais de três parâmetros
    (CONTRIBUTING §4.2). Todos são opcionais: a fachada só substitui os que
    vierem preenchidos.
    """
    usuario_controller: UsuarioController | None = None
    autenticacao_controller: AutenticacaoController | None = None
    contrato_controller: ContratoController | None = None
    relatorio_controller: RelatorioController | None = None
    evidencia_repositorio: EvidenciaRepositorio | None = None
