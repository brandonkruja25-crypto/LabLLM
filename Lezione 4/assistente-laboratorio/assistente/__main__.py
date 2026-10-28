"""Avvio: python -m assistente."""

import logging
import os
import sys
from collections.abc import Mapping

from dotenv import load_dotenv

from assistente.configurazione import ErroreConfigurazione, carica_configurazione
from assistente.conversazione import Conversazione
from assistente.grafo import crea_grafo
from assistente.modello import crea_modello, verifica_modello
from assistente.strumenti import crea_strumento_orologio
from assistente.terminale import esegui_chat


def main(ambiente: Mapping[str, str] | None = None) -> int:
    if ambiente is None:
        load_dotenv()
        ambiente = os.environ
    try:
        config = carica_configurazione(ambiente)
        logging.basicConfig(
            stream=sys.stderr,
            level=config.livello_log,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
        avviso = verifica_modello(config.base_url, config.modello)
    except ErroreConfigurazione as errore:
        print(f"Errore di configurazione: {errore}", file=sys.stderr)
        return 1
    if avviso:
        print(avviso, file=sys.stderr)

    strumenti = [crea_strumento_orologio(config.fuso_predefinito)]
    grafo = crea_grafo(crea_modello(config, strumenti), strumenti, config.max_passaggi)
    print(f"Assistente del laboratorio — modello {config.modello} su {config.base_url}")
    print("Scrivi «esci» per terminare.")
    esegui_chat(Conversazione(grafo, config.base_url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
