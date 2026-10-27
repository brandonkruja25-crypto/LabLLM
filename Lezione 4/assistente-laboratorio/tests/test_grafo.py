from langchain_core.messages import AIMessage, HumanMessage

from assistente.grafo import RISPOSTA_FISSA, crea_grafo_fisso


def test_grafo_fisso_aggiunge_la_risposta_prevista():
    risultato = crea_grafo_fisso().invoke({"messages": [HumanMessage("ciao")]})
    assert [type(m) for m in risultato["messages"]] == [HumanMessage, AIMessage]
    assert risultato["messages"][-1].content == RISPOSTA_FISSA == "Il grafo è in esecuzione."


def test_grafo_fisso_esegue_il_nodo_una_volta():
    passi = list(crea_grafo_fisso().stream({"messages": [HumanMessage("x")]}, stream_mode="updates"))
    assert [list(p) for p in passi] == [["risposta"]]
