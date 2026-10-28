from datetime import datetime, timezone

import pytest

from assistente.strumenti import crea_strumento_orologio, ora_corrente_testo, valida_fuso

ISTANTE_INVERNO = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
ISTANTE_ESTATE = datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
TOKYO_INVERNO = "2026-01-15T21:00:00+09:00 (Asia/Tokyo)"
ROMA_INVERNO = "2026-01-15T13:00:00+01:00 (Europe/Rome)"


@pytest.mark.parametrize(
    ("fuso", "istante", "atteso"),
    [
        ("Europe/Rome", ISTANTE_INVERNO, ROMA_INVERNO),
        ("Europe/Rome", ISTANTE_ESTATE, "2026-07-15T14:00:00+02:00 (Europe/Rome)"),
        ("Asia/Tokyo", ISTANTE_INVERNO, TOKYO_INVERNO),
        ("UTC", ISTANTE_INVERNO, "2026-01-15T12:00:00+00:00 (UTC)"),
        (None, ISTANTE_INVERNO, ROMA_INVERNO),
        (" Asia/Tokyo ", ISTANTE_INVERNO, TOKYO_INVERNO),
    ],
    ids=["roma-inverno", "roma-estate", "tokyo", "utc", "default", "spazi"],
)
def test_ora_nel_fuso(fuso, istante, atteso):
    assert ora_corrente_testo(fuso, "Europe/Rome", istante) == atteso


@pytest.mark.parametrize("fuso", ["Tokyo", "UTC+2", "", "../etc/passwd", "Europe"])
def test_fuso_non_valido_restituisce_errore_testuale(fuso):
    risultato = ora_corrente_testo(fuso, "Europe/Rome", ISTANTE_INVERNO)
    assert risultato.startswith("Errore:")
    assert repr(fuso) in risultato
    assert "Asia/Tokyo" in risultato


@pytest.mark.parametrize("fuso", ["Tokyo", "", "   ", "../etc/passwd"])
def test_valida_fuso_solleva_value_error(fuso):
    with pytest.raises(ValueError):
        valida_fuso(fuso)


def test_strumento_langchain():
    strumento = crea_strumento_orologio("Europe/Rome", orologio=lambda: ISTANTE_INVERNO)
    assert strumento.name == "ora_corrente"
    for testo in ("Europe/Rome", "Asia/Tokyo", "America/New_York", "UTC"):
        assert testo in strumento.description
    assert strumento.invoke({"fuso_orario": "Asia/Tokyo"}) == TOKYO_INVERNO
    assert strumento.invoke({}) == ROMA_INVERNO


def test_schema_inviato_al_modello_descrive_il_parametro():
    from langchain_core.utils.function_calling import convert_to_openai_tool

    schema = convert_to_openai_tool(crea_strumento_orologio("Europe/Rome"))
    parametro = schema["function"]["parameters"]["properties"]["fuso_orario"]
    assert "Asia/Tokyo" in parametro["description"]
    assert "città" in parametro["description"]
    assert schema["function"]["parameters"].get("required", []) == []
