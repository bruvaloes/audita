"""Utilitário para padronização e conversão de datas e horários (NF006).

Padroniza:
- Formato de data brasileira: dd/mm/aaaa
- Formato de data e horário: dd/mm/aaaa hh:mm (fuso horário de Brasília - America/Sao_Paulo)
- Leitura e parsing de datas em vigências e consultas
"""
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from excecao.validacao_error import DataInvalidaError

try:
    FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    # Sem a base de fusos (ex.: Windows sem o pacote tzdata): Brasília é UTC-3.
    FUSO_BRASILIA = timezone(timedelta(hours=-3), name="BRT")
FORMATO_DATA = "%d/%m/%Y"
FORMATO_DATA_HORA = "%d/%m/%Y %H:%M"


def formatar_data(d: date | datetime | None) -> str:
    """Formata uma data ou datetime para o padrão brasileiro dd/mm/aaaa."""
    if d is None:
        return ""
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime(FORMATO_DATA)


def formatar_data_hora(dt: datetime | None) -> str:
    """Formata data e horário para dd/mm/aaaa hh:mm em 24h, no fuso de Brasília."""
    if dt is None:
        return ""
    if dt.tzinfo is not None:
        dt = dt.astimezone(FUSO_BRASILIA)
    return dt.strftime(FORMATO_DATA_HORA)


def parsear_data(texto: str, campo: str) -> date:
    """Converte string no formato dd/mm/aaaa para date.

    Levanta DataInvalidaError citando o campo caso o formato ou a data sejam inválidos.
    """
    if not isinstance(texto, str):
        raise DataInvalidaError(campo)

    limpo = texto.strip()
    if len(limpo) != 10 or limpo[2] != "/" or limpo[5] != "/":
        raise DataInvalidaError(campo)

    try:
        return datetime.strptime(limpo, FORMATO_DATA).date()
    except ValueError:
        raise DataInvalidaError(campo)
