"""Prove reali con LM Studio: python -m pytest -m lmstudio -v (richiede .env e il server attivo)."""

import os

import pytest
from dotenv import load_dotenv

from assistente.configurazione import carica_configurazione
from assistente.conversazione import Conversazione
from assistente.grafo import crea_grafo
from assistente.modello import crea_modello, verifica_modello

pytestmark = pytest.mark.lmstudio


@pytest.fixture
def conversazione():
    load_dotenv()
    config = carica_configurazione(os.environ)
    assert verifica_modello(config.base_url, config.modello) is None, "LM Studio non risponde"
    return Conversazione(crea_grafo(crea_modello(config), max_passaggi=config.max_passaggi), config.base_url)


def test_due_turni_con_il_modello_reale(conversazione):
    conversazione.invia("Mi chiamo Ada.")
    esito = conversazione.invia("Come mi chiamo?")
    assert "Ada" in esito.risposta
