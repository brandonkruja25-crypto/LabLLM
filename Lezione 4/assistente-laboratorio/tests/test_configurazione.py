import pytest

from assistente.configurazione import ErroreConfigurazione, carica_configurazione

MINIMO = {
    "LMSTUDIO_BASE_URL": "http://localhost:1234/v1",
    "LMSTUDIO_MODEL": "google/gemma-4-e2b",
}


def test_valori_minimi_e_default():
    config = carica_configurazione(MINIMO)
    assert config.base_url == "http://localhost:1234/v1"
    assert config.modello == "google/gemma-4-e2b"
    assert config.fuso_predefinito == "Europe/Rome"
    assert config.max_passaggi == 6
    assert config.livello_log == "WARNING"


@pytest.mark.parametrize("variabile", ["LMSTUDIO_BASE_URL", "LMSTUDIO_MODEL"])
@pytest.mark.parametrize("valore", [None, "  "])
def test_variabile_obbligatoria_mancante(variabile, valore):
    ambiente = dict(MINIMO)
    if valore is None:
        del ambiente[variabile]
    else:
        ambiente[variabile] = valore
    with pytest.raises(ErroreConfigurazione, match=variabile):
        carica_configurazione(ambiente)


@pytest.mark.parametrize("valore", ["0", "-1", "sei"])
def test_max_passaggi_non_valido(valore):
    with pytest.raises(ErroreConfigurazione, match="MAX_PASSAGGI"):
        carica_configurazione({**MINIMO, "MAX_PASSAGGI": valore})


def test_livello_log_non_valido():
    with pytest.raises(ErroreConfigurazione, match="LIVELLO_LOG"):
        carica_configurazione({**MINIMO, "LIVELLO_LOG": "verbose"})
    assert carica_configurazione({**MINIMO, "LIVELLO_LOG": "info"}).livello_log == "INFO"


def test_fuso_predefinito_non_valido():
    with pytest.raises(ErroreConfigurazione, match="FUSO_ORARIO_PREDEFINITO"):
        carica_configurazione({**MINIMO, "FUSO_ORARIO_PREDEFINITO": "Roma"})


@pytest.mark.parametrize("valore", ["localhost:1234/v1", "http://local host:1234/v1", "ftp://localhost/v1", "http://"])
def test_base_url_non_valido(valore):
    with pytest.raises(ErroreConfigurazione, match="LMSTUDIO_BASE_URL"):
        carica_configurazione({**MINIMO, "LMSTUDIO_BASE_URL": valore})
