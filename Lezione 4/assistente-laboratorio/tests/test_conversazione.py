import openai
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda

from assistente.conversazione import Conversazione, ErroreModello
from assistente.grafo import crea_grafo

BASE_URL = "http://localhost:1234/v1"


class ConnessioneRifiutata(openai.APIConnectionError):
    def __init__(self):
        Exception.__init__(self, "Connection refused")


class ModelloNonCaricato(openai.APIStatusError):
    def __init__(self):
        Exception.__init__(self, "Error code: 404 - model not loaded")


def modello_a_copione(*passi):
    """Modello finto: ogni passo è un AIMessage da restituire o un'eccezione da sollevare."""
    coda = list(passi)

    def rispondi(messaggi):
        passo = coda.pop(0)
        if isinstance(passo, Exception):
            raise passo
        return passo

    return RunnableLambda(rispondi)


def conversazione(*passi):
    return Conversazione(crea_grafo(modello_a_copione(*passi)), BASE_URL)


def test_due_turni_conservano_la_cronologia():
    conv = conversazione(AIMessage("Ciao Ada!"), AIMessage("Ti chiami Ada."))
    assert conv.invia("Mi chiamo Ada.").risposta == "Ciao Ada!"
    assert conv.invia("Come mi chiamo?").risposta == "Ti chiami Ada."
    assert [type(m) for m in conv.cronologia] == [HumanMessage, AIMessage, HumanMessage, AIMessage]
    assert [m.content for m in conv.cronologia] == ["Mi chiamo Ada.", "Ciao Ada!", "Come mi chiamo?", "Ti chiami Ada."]


@pytest.mark.parametrize("errore", [ConnessioneRifiutata(), ModelloNonCaricato()], ids=["connessione", "http"])
def test_errore_del_modello_ripristina_la_cronologia(errore):
    conv = conversazione(AIMessage("Ciao!"), errore, AIMessage("Eccomi."))
    conv.invia("ciao")
    prima = list(conv.cronologia)

    with pytest.raises(ErroreModello) as eccezione:
        conv.invia("ci sei?")
    assert BASE_URL in str(eccezione.value)
    assert "LM Studio sia avviato" in str(eccezione.value)
    assert conv.cronologia == prima

    assert conv.invia("ci sei?").risposta == "Eccomi."
    assert len(conv.cronologia) == 4
