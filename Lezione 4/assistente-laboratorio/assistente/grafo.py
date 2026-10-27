"""Grafo LangGraph della conversazione: stato, nodi e instradamento."""

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

RISPOSTA_FISSA = "Il grafo è in esecuzione."


class StatoConversazione(TypedDict):
    """Stato del grafo: i messaggi vengono aggiunti, non sostituiti."""

    messages: Annotated[list[AnyMessage], add_messages]


def crea_grafo_fisso() -> CompiledStateGraph:
    """Grafo minimo senza modello: un nodo che restituisce sempre la stessa risposta."""

    def risposta(stato: StatoConversazione) -> dict:
        return {"messages": [AIMessage(RISPOSTA_FISSA)]}

    costruttore = StateGraph(StatoConversazione)
    costruttore.add_node("risposta", risposta)
    costruttore.add_edge(START, "risposta")
    costruttore.add_edge("risposta", END)
    return costruttore.compile()
