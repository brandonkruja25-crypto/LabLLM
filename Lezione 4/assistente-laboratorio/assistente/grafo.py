"""Grafo LangGraph della conversazione: stato, nodi e instradamento."""

import logging
import time
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

log = logging.getLogger(__name__)

PROMPT_SISTEMA = (
    "Sei l'assistente del laboratorio e rispondi in italiano, in modo breve e chiaro. "
    "Quando servono la data o l'ora attuali usa sempre lo strumento ora_corrente: "
    "non inventarle e non dedurle dalla conversazione."
)


class StatoConversazione(TypedDict):
    """Stato del grafo: i messaggi vengono aggiunti, non sostituiti."""

    messages: Annotated[list[AnyMessage], add_messages]


def crea_grafo(
    modello: Runnable, strumenti: Sequence[BaseTool] = (), max_passaggi: int = 6
) -> CompiledStateGraph:
    """Grafo START → llm → END."""

    def llm(stato: StatoConversazione) -> dict:
        log.info("Inizio chiamata al modello (%d messaggi)", len(stato["messages"]))
        inizio = time.perf_counter()
        risposta = modello.invoke([SystemMessage(PROMPT_SISTEMA), *stato["messages"]])
        log.info("Fine chiamata al modello in %.2f s", time.perf_counter() - inizio)
        return {"messages": [risposta]}

    costruttore = StateGraph(StatoConversazione)
    costruttore.add_node("llm", llm)
    costruttore.add_edge(START, "llm")
    costruttore.add_edge("llm", END)
    return costruttore.compile()
