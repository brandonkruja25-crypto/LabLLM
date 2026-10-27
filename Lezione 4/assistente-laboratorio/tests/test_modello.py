import pytest

from assistente.configurazione import ErroreConfigurazione
from assistente.modello import verifica_modello

BASE_URL = "http://localhost:1234/v1"


def test_verifica_modello_presente():
    assert verifica_modello(BASE_URL, "google/gemma-4-e2b", elenca=lambda url: ["google/gemma-4-e2b"]) is None


def test_verifica_modello_assente():
    with pytest.raises(ErroreConfigurazione) as errore:
        verifica_modello(BASE_URL, "inventato", elenca=lambda url: ["google/gemma-4-e2b", "altro/modello"])
    messaggio = str(errore.value)
    assert "inventato" in messaggio
    assert "google/gemma-4-e2b" in messaggio and "altro/modello" in messaggio


def test_verifica_server_irraggiungibile():
    def elenca(url):
        raise OSError("Connection refused")

    avviso = verifica_modello(BASE_URL, "google/gemma-4-e2b", elenca=elenca)
    assert isinstance(avviso, str) and BASE_URL in avviso
