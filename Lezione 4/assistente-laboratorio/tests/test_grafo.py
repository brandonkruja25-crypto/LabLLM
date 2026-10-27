import logging

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from assistente.grafo import crea_grafo


def modello_finto(*risposte):
    return GenericFakeChatModel(messages=iter(risposte))


def test_grafo_passa_dal_nodo_llm():
    grafo = crea_grafo(modello_finto(AIMessage("Ciao!")))
    passi = list(grafo.stream({"messages": [HumanMessage("ciao")]}, stream_mode="updates"))
    assert [list(p) for p in passi] == [["llm"]]
    assert passi[-1]["llm"]["messages"][-1].content == "Ciao!"


def test_log_della_chiamata_al_modello(caplog):
    caplog.set_level(logging.INFO, logger="assistente")
    crea_grafo(modello_finto(AIMessage("Ciao!"))).invoke({"messages": [HumanMessage("ciao")]})
    testo = caplog.text.lower()
    assert "inizio chiamata al modello" in testo
    assert "fine chiamata al modello" in testo
