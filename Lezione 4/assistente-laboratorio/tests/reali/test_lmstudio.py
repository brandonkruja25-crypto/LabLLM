"""Prove reali con LM Studio: python -m pytest -m lmstudio -v (richiede .env e il server attivo)."""

import os
import re

import pytest
from dotenv import load_dotenv

from assistente.configurazione import carica_configurazione
from assistente.conversazione import Conversazione
from assistente.grafo import crea_grafo
from assistente.modello import crea_modello, verifica_modello
from assistente.strumenti import crea_strumento_orologio

pytestmark = pytest.mark.lmstudio


@pytest.fixture
def conversazione():
    load_dotenv()
    config = carica_configurazione(os.environ)
    assert verifica_modello(config.base_url, config.modello) is None, "LM Studio non risponde"
    strumenti = [crea_strumento_orologio(config.fuso_predefinito)]
    grafo = crea_grafo(crea_modello(config, strumenti), strumenti, config.max_passaggi)
    return Conversazione(grafo, config.base_url)


def test_due_turni_con_il_modello_reale(conversazione):
    conversazione.invia("Mi chiamo Ada.")
    esito = conversazione.invia("Come mi chiamo?")
    assert "Ada" in esito.risposta


def test_domanda_sull_ora_usa_lo_strumento(conversazione):
    esito = conversazione.invia("Che ore sono adesso a Tokyo?")
    print(esito)
    tokyo = [
        c for c in esito.chiamate
        if c.nome == "ora_corrente" and (c.argomenti.get("fuso_orario") or "").strip() == "Asia/Tokyo"
    ]
    assert tokyo, f"nessuna chiamata a ora_corrente per Asia/Tokyo: {esito.chiamate}"
    risultato = tokyo[-1].risultato
    assert not risultato.startswith("Errore:")
    ora_minuti = re.search(r"T(\d{2}:\d{2})", risultato).group(1)
    assert ora_minuti in esito.risposta


def test_domanda_ordinaria_senza_strumento(conversazione):
    esito = conversazione.invia("Qual è la capitale della Francia?")
    print(esito)
    assert esito.chiamate == []
    assert "Parigi" in esito.risposta
