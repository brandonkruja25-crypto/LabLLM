"""Configurazione letta dalle variabili d'ambiente e validata all'avvio."""

from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse

from assistente.strumenti import valida_fuso

LIVELLI_LOG = ("DEBUG", "INFO", "WARNING", "ERROR")


class ErroreConfigurazione(Exception):
    """Configurazione mancante o non valida; il messaggio nomina la variabile."""


@dataclass(frozen=True)
class Configurazione:
    base_url: str
    modello: str
    fuso_predefinito: str
    max_passaggi: int
    livello_log: str


def _obbligatoria(ambiente: Mapping[str, str], nome: str) -> str:
    valore = (ambiente.get(nome) or "").strip()
    if not valore:
        raise ErroreConfigurazione(f"Variabile {nome} mancante: impostala nel file .env o nell'ambiente.")
    return valore


def carica_configurazione(ambiente: Mapping[str, str]) -> Configurazione:
    base_url = _obbligatoria(ambiente, "LMSTUDIO_BASE_URL")
    indirizzo = urlparse(base_url)
    if indirizzo.scheme not in ("http", "https") or not indirizzo.netloc or any(c.isspace() for c in base_url):
        raise ErroreConfigurazione(
            f"LMSTUDIO_BASE_URL non valido: {base_url!r}. Serve un indirizzo http, per esempio http://localhost:1234/v1."
        )
    modello = _obbligatoria(ambiente, "LMSTUDIO_MODEL")

    fuso = (ambiente.get("FUSO_ORARIO_PREDEFINITO") or "Europe/Rome").strip()
    try:
        valida_fuso(fuso)
    except ValueError:
        raise ErroreConfigurazione(
            f"FUSO_ORARIO_PREDEFINITO non valido: {fuso!r}. Usa un nome IANA, per esempio Europe/Rome."
        ) from None

    testo_passaggi = (ambiente.get("MAX_PASSAGGI") or "6").strip()
    try:
        max_passaggi = int(testo_passaggi)
    except ValueError:
        max_passaggi = 0
    if max_passaggi < 1:
        raise ErroreConfigurazione(f"MAX_PASSAGGI non valido: {testo_passaggi!r}. Serve un intero maggiore o uguale a 1.")

    livello_log = (ambiente.get("LIVELLO_LOG") or "WARNING").strip().upper()
    if livello_log not in LIVELLI_LOG:
        raise ErroreConfigurazione(f"LIVELLO_LOG non valido: {livello_log!r}. Valori ammessi: {', '.join(LIVELLI_LOG)}.")

    return Configurazione(base_url, modello, fuso, max_passaggi, livello_log)
