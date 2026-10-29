import logging
from datetime import datetime
from pathlib import Path

from log.log_auditoria import LogAuditoria
from log.operacao_log import OperacaoLog
from log.registro_log import FORMATO_DATA_HORA, RegistroLog

SEPARADOR = " | "


class LogAuditoriaAdapter(LogAuditoria):
    """Adapter GoF: adapta a biblioteca padrão `logging` para a interface `LogAuditoria`.

    O restante da aplicação só conhece a interface LogAuditoria; os detalhes
    específicos da biblioteca (Logger, FileHandler, Formatter, buffers)
    permanecem completamente isolados neste Adapter.
    """

    def __init__(
        self,
        caminho_arquivo: str = "auditoria.log",
        logger_name: str | None = None,
    ) -> None:
        self._caminho_arquivo = Path(caminho_arquivo)
        nome = logger_name or f"audita.auditoria.{id(self)}"
        self._logger = logging.getLogger(nome)
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        # Limpa handlers anteriores para evitar duplicações caso o nome seja reutilizado
        for handler in list(self._logger.handlers):
            self._logger.removeHandler(handler)
            handler.close()

        # Garante a existência do diretório pai se especificado
        if self._caminho_arquivo.parent and not self._caminho_arquivo.parent.exists():
            self._caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        self._handler = logging.FileHandler(self._caminho_arquivo, encoding="utf-8")
        self._handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(self._handler)

    def registrar(self, registro: RegistroLog) -> None:
        """Converte a chamada de domínio em mensagem formatada para o logger."""
        usuario_str = registro.usuario if registro.usuario is not None else "-"
        linha = (
            f"{registro.data_hora_formatada}{SEPARADOR}"
            f"{registro.operacao.value}{SEPARADOR}"
            f"{usuario_str}{SEPARADOR}"
            f"{registro.detalhes}"
        )
        self._logger.info(linha)
        # Flush imediato para garantir gravação em menos de 1 segundo (NF004)
        self._handler.flush()

    def listar(self) -> list[RegistroLog]:
        """Recupera os registros gravados a partir do arquivo persistido pelo logger."""
        if not self._caminho_arquivo.exists():
            return []

        registros: list[RegistroLog] = []
        with open(self._caminho_arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split(SEPARADOR, maxsplit=3)
                if len(partes) == 4:
                    data_hora_str, op_str, usr_str, detalhes = partes
                    usuario = None if usr_str == "-" else usr_str
                    try:
                        operacao = OperacaoLog(op_str)
                        data_hora = datetime.strptime(data_hora_str, FORMATO_DATA_HORA)
                        registros.append(
                            RegistroLog(
                                usuario=usuario,
                                operacao=operacao,
                                data_hora=data_hora,
                                detalhes=detalhes,
                            )
                        )
                    except ValueError:
                        continue
        return registros

    def fechar(self) -> None:
        """Libera o handler do arquivo associado ao logger."""
        self._handler.close()
        self._logger.removeHandler(self._handler)
