"""Collegamento al modello servito da LM Studio tramite l'API compatibile con OpenAI."""

import json
import urllib.request
from collections.abc import Callable, Sequence

from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from assistente.configurazione import Configurazione, ErroreConfigurazione

# LM Studio non richiede una chiave: il client ne vuole comunque una, quindi si usa un segnaposto.
CHIAVE_SEGNAPOSTO = "lm-studio"


def crea_modello(config: Configurazione, strumenti: Sequence[BaseTool] = ()) -> Runnable:
    modello = ChatOpenAI(base_url=config.base_url, model=config.modello, api_key=CHIAVE_SEGNAPOSTO)
    return modello.bind_tools(list(strumenti)) if strumenti else modello


def elenca_modelli(base_url: str, timeout: float = 5.0) -> list[str]:
    """Identificativi restituiti da GET {base_url}/models; OSError se il server non risponde."""
    with urllib.request.urlopen(f"{base_url.rstrip('/')}/models", timeout=timeout) as risposta:
        dati = json.load(risposta)
    return [voce["id"] for voce in dati.get("data", [])]


def verifica_modello(
    base_url: str, modello: str, elenca: Callable[[str], list[str]] = elenca_modelli
) -> str | None:
    """None se il modello è disponibile; un avviso se il server non risponde.

    Solleva ErroreConfigurazione se il server risponde ma il modello non è nell'elenco.
    """
    try:
        disponibili = elenca(base_url)
    except OSError as errore:
        return (
            f"Avviso: il server su {base_url} non risponde ({errore}). "
            "Avvia LM Studio e il suo server: potrai riprovare durante la sessione."
        )
    if modello not in disponibili:
        raise ErroreConfigurazione(
            f"LMSTUDIO_MODEL={modello!r} non è tra i modelli di {base_url}. "
            f"Disponibili: {', '.join(disponibili) or '(nessuno)'}."
        )
    return None
