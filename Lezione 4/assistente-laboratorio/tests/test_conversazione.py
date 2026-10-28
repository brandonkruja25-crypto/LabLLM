import openai
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from assistente.conversazione import ChiamataStrumento, Conversazione, ErroreModello
from assistente.grafo import crea_grafo
from assistente.strumenti import crea_strumento_orologio
from tests.finti import ISTANTE_INVERNO, TOKYO_INVERNO, modello_a_copione, richiesta_strumento

BASE_URL = "http://localhost:1234/v1"


class ConnessioneRifiutata(openai.APIConnectionError):
    def __init__(self):
        Exception.__init__(self, "Connection error.")


class ModelloNonCaricato(openai.APIStatusError):
    def __init__(self):
        Exception.__init__(self, "Error code: 404 - model not loaded")


STRUMENTI = [crea_strumento_orologio("Europe/Rome", orologio=lambda: ISTANTE_INVERNO)]


def conversazione(*passi):
    return Conversazione(crea_grafo(modello_a_copione(*passi), STRUMENTI), BASE_URL)


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
    assert ".." not in str(eccezione.value)
    assert conv.cronologia == prima

    assert conv.invia("ci sei?").risposta == "Eccomi."
    assert len(conv.cronologia) == 4


def test_esito_con_chiamate():
    conv = conversazione(richiesta_strumento(), AIMessage("A Tokyo sono le 21:00."))
    esito = conv.invia("Che ore sono a Tokyo?")
    assert esito.chiamate == [ChiamataStrumento("ora_corrente", {"fuso_orario": "Asia/Tokyo"}, TOKYO_INVERNO)]
    assert esito.risposta == "A Tokyo sono le 21:00."
    assert not esito.limite_raggiunto


def test_limite_ripristina_la_cronologia():
    passi = [richiesta_strumento(id_chiamata=f"call_{n}") for n in range(2)] + [AIMessage("Ciao!")]
    modello = modello_a_copione(*passi)
    conv = Conversazione(crea_grafo(modello, STRUMENTI, max_passaggi=2), BASE_URL)

    esito = conv.invia("Che ore sono a Tokyo?")
    assert esito.limite_raggiunto and esito.risposta is None
    assert len(esito.chiamate) == 1
    assert conv.cronologia == []

    assert conv.invia("ciao").risposta == "Ciao!"
    assert [m.content for m in conv.cronologia] == ["ciao", "Ciao!"]


def test_chiamata_con_argomenti_non_json_mostrata():
    from tests.finti import richiesta_non_valida

    esito = conversazione(richiesta_non_valida(), AIMessage("Riprovo.")).invia("Che ore sono a Tokyo?")
    [chiamata] = esito.chiamate
    assert chiamata.nome == "ora_corrente"
    assert chiamata.argomenti == {"argomenti_non_validi": "{fuso_orario: Asia/Tokyo"}
    assert chiamata.risultato.startswith("Errore:")
