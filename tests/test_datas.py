"""Testes do utilitário de datas e horários (NF006)."""
from datetime import date, datetime, timezone, timedelta
import pytest


from controle.utils.datas import formatar_data, formatar_data_hora, parsear_data
from excecao.validacao_error import DataInvalidaError


def test_formatar_data_padrao_brasileiro():
    d = date(2026, 10, 28)
    assert formatar_data(d) == "28/10/2026"


def test_formatar_data_com_datetime():
    dt = datetime(2026, 3, 5, 14, 30)
    assert formatar_data(dt) == "05/03/2026"


def test_formatar_data_com_none():
    assert formatar_data(None) == ""


def test_formatar_data_hora_24h_sem_fuso():
    dt = datetime(2026, 10, 28, 14, 5)
    assert formatar_data_hora(dt) == "28/10/2026 14:05"


def test_formatar_data_hora_com_none():
    assert formatar_data_hora(None) == ""


def test_formatar_data_hora_conversao_fuso_brasilia():
    # UTC 17:30 equivale a 14:30 em Brasília (UTC-3)
    dt_utc = datetime(2026, 10, 28, 17, 30, tzinfo=timezone.utc)
    assert formatar_data_hora(dt_utc) == "28/10/2026 14:30"


def test_parsear_data_valida():
    resultado = parsear_data("28/10/2026", "vigência início")
    assert resultado == date(2026, 10, 28)


def test_parsear_data_com_espacos_laterais():
    resultado = parsear_data("  15/01/2025  ", "vigência fim")
    assert resultado == date(2025, 1, 15)


def test_parsear_data_formato_iso_rejeitado():
    with pytest.raises(DataInvalidaError) as exc_info:
        parsear_data("2026-10-28", "vigência início")
    assert "vigência início" in str(exc_info.value)
    assert "dd/mm/aaaa" in str(exc_info.value)


def test_parsear_data_invalida_mes_ou_dia_inexistente():
    with pytest.raises(DataInvalidaError) as exc_info:
        parsear_data("31/02/2026", "vigência fim")
    assert "vigência fim" in str(exc_info.value)


def test_parsear_data_texto_vazio_ou_invalido():
    with pytest.raises(DataInvalidaError) as exc_info:
        parsear_data("abc", "data")
    assert "data" in str(exc_info.value)
