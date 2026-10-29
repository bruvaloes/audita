from dataclasses import dataclass
from datetime import datetime

from log.operacao_log import OperacaoLog

FORMATO_DATA_HORA = "%d/%m/%Y %H:%M:%S"


@dataclass(frozen=True)
class RegistroLog:
    """Registro imutável de auditoria (NF004).

    Campos obrigatórios: usuário, operação, data_hora e detalhes.
    A imutabilidade é garantida por meio de frozen=True (não permite alteração
    de nenhum atributo após a criação).
    """
    usuario: str | None
    operacao: OperacaoLog
    data_hora: datetime
    detalhes: str

    @property
    def data_hora_formatada(self) -> str:
        """Retorna a data e hora formatada no padrão dd/mm/aaaa hh:mm:ss."""
        return self.data_hora.strftime(FORMATO_DATA_HORA)

    def __str__(self) -> str:
        usr = self.usuario if self.usuario else "ANONIMO"
        return (
            f"[{self.data_hora_formatada}] [{self.operacao.value}] "
            f"usuario={usr} - {self.detalhes}"
        )
