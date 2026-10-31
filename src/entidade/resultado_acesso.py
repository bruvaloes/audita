from enum import Enum


class ResultadoAcesso(Enum):
    SUCESSO = "SUCESSO"
    CREDENCIAIS_INVALIDAS = "CREDENCIAIS_INVALIDAS"
    # Ainda não é gerado: o bloqueio por tentativas é a issue #57.
    BLOQUEADO = "BLOQUEADO"
