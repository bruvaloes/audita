from dataclasses import dataclass
from datetime import datetime

from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso


@dataclass
class Acesso:
    """Registro de uma tentativa de login, com sucesso ou falha.

    `usuario_id` fica vazio quando nenhum usuário foi identificado, e
    `perfil` é o perfil informado na tentativa (vazio se não for um perfil
    válido), não o do cadastro. O texto digitado como identificador não é
    guardado, pois pode conter CPF ou uma senha digitada no campo errado.
    """
    id: int
    usuario_id: int | None
    perfil: Perfil | None
    data_hora: datetime
    resultado: ResultadoAcesso
