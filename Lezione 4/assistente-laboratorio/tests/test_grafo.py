import logging

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda

from assistente.grafo import crea_grafo, instrada
from assistente.strumenti import crea_strumento_orologio
from tests.finti import ISTANTE_INVERNO, TOKYO_INVERNO, modello_a_copione, richiesta_strumento

STRUMENTI = [crea_strumento_orologio("Europe/Rome", orologio=lambda: ISTANTE_INVERNO)]
INGRESSO = {"messages": [HumanMessage("Che ore sono a Tokyo?")], "passaggi": 0, "limite_raggiunto": False}


def nodi_visitati(grafo, ingresso=INGRESSO):
    return [nodo for passo in grafo.stream(ingresso, stream_mode="updates") for nodo in passo]


def test_grafo_passa_dal_nodo_llm():
    grafo = crea_grafo(GenericFakeChatModel(messages=iter([AIMessage("Ciao!")])))
    passi = list(grafo.stream({"messages": [HumanMessage("ciao")]}, stream_mode="updates"))
    assert [list(p) for p in passi] == [["llm"]]
    assert passi[-1]["llm"]["messages"][-1].content == "Ciao!"


def test_log_della_chiamata_al_modello(caplog):
    caplog.set_level(logging.INFO, logger="assistente")
    crea_grafo(GenericFakeChatModel(messages=iter([AIMessage("Ciao!")]))).invoke({"messages": [HumanMessage("ciao")]})
    testo = caplog.text.lower()
    assert "inizio chiamata al modello" in testo
    assert "fine chiamata al modello" in testo


def test_percorso_con_strumento():
    modello = modello_a_copione(richiesta_strumento(), AIMessage("A Tokyo sono le 21:00."))
    grafo = crea_grafo(modello, STRUMENTI)
    assert nodi_visitati(grafo) == ["llm", "strumenti", "llm"]

    modello = modello_a_copione(richiesta_strumento(), AIMessage("A Tokyo sono le 21:00."))
    risultato = crea_grafo(modello, STRUMENTI).invoke(INGRESSO)
    [risposta_strumento] = [m for m in risultato["messages"] if isinstance(m, ToolMessage)]
    assert risposta_strumento.tool_call_id == "call_1"
    assert risposta_strumento.content == TOKYO_INVERNO
    assert risultato["messages"][-1].content == "A Tokyo sono le 21:00."


def test_percorso_senza_strumento():
    grafo = crea_grafo(modello_a_copione(AIMessage("Parigi.")), STRUMENTI)
    assert nodi_visitati(grafo) == ["llm"]


def test_limite_di_passaggi():
    chiamate = []

    def chiede_sempre(messaggi):
        chiamate.append(1)
        return richiesta_strumento(id_chiamata=f"call_{len(chiamate)}")

    grafo = crea_grafo(RunnableLambda(chiede_sempre), STRUMENTI, max_passaggi=3)
    visitati = nodi_visitati(grafo)
    assert visitati.count("llm") == 3
    assert visitati.count("strumenti") == 2

    chiamate.clear()
    assert crea_grafo(RunnableLambda(chiede_sempre), STRUMENTI, max_passaggi=3).invoke(INGRESSO)["limite_raggiunto"] is True


@pytest.mark.parametrize(
    "richiesta",
    [richiesta_strumento(nome="meteo"), richiesta_strumento(argomenti={"timezone": "Asia/Tokyo"})],
    ids=["strumento-sconosciuto", "argomenti-errati"],
)
def test_strumento_sconosciuto_e_argomenti_errati(richiesta):
    modello = modello_a_copione(richiesta, AIMessage("Non riesco."))
    risultato = crea_grafo(modello, STRUMENTI).invoke(INGRESSO)
    [risposta_strumento] = [m for m in risultato["messages"] if isinstance(m, ToolMessage)]
    assert risposta_strumento.content.startswith("Errore:")
    assert risposta_strumento.tool_call_id == "call_1"
    assert risultato["messages"][-1].content == "Non riesco."


def test_log_della_chiamata_allo_strumento(caplog):
    caplog.set_level(logging.INFO, logger="assistente")
    modello = modello_a_copione(richiesta_strumento(), AIMessage("Sono le 21."))
    crea_grafo(modello, STRUMENTI).invoke(INGRESSO)
    assert "ora_corrente" in caplog.text
    assert "Asia/Tokyo" in caplog.text
    assert TOKYO_INVERNO in caplog.text


@pytest.mark.parametrize(
    ("messaggio", "passaggi", "atteso"),
    [
        (richiesta_strumento(), 1, "strumenti"),
        (richiesta_strumento(), 3, "fine"),
        (AIMessage("Ciao"), 1, "fine"),
        (AIMessage("Ciao"), 3, "fine"),
    ],
    ids=["tool-sotto-limite", "tool-al-limite", "testo-sotto-limite", "testo-al-limite"],
)
def test_instrada(messaggio, passaggi, atteso):
    stato = {"messages": [HumanMessage("x"), messaggio], "passaggi": passaggi, "limite_raggiunto": False}
    assert instrada(stato, max_passaggi=3) == atteso


def test_prompt_di_sistema_chiede_il_fuso_del_luogo():
    from assistente.grafo import PROMPT_SISTEMA

    assert "ora_corrente" in PROMPT_SISTEMA
    assert "fuso_orario" in PROMPT_SISTEMA and "Asia/Tokyo" in PROMPT_SISTEMA
