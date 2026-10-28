"""Grafo LangGraph della conversazione: stato, nodi e instradamento.

START → llm ──(richieste di tool e passaggi < max?)──sì──→ strumenti ──→ llm
              └──no──→ END
"""

import logging
import time
from collections.abc import Sequence
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, SystemMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

log = logging.getLogger(__name__)

PROMPT_SISTEMA = (
    "Sei l'assistente del laboratorio e rispondi in italiano, in modo breve e chiaro. "
    "Quando servono la data o l'ora attuali usa sempre lo strumento ora_corrente: "
    "non inventarle e non dedurle dalla conversazione. Se la domanda riguarda una città o un "
    "paese, passa a ora_corrente il parametro fuso_orario con il nome IANA di quel luogo "
    "(per esempio Asia/Tokyo per Tokyo)."
)


class StatoConversazione(TypedDict):
    """Stato del grafo: i messaggi vengono aggiunti, non sostituiti.

    passaggi conta le chiamate al nodo llm nel turno; limite_raggiunto diventa vero quando il
    modello chiede ancora uno strumento dopo l'ultimo passaggio consentito.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    passaggi: int
    limite_raggiunto: bool


def _richieste_di_tool(stato: StatoConversazione) -> list:
    ultimo = stato["messages"][-1]
    return ultimo.tool_calls if isinstance(ultimo, AIMessage) else []


def instrada(stato: StatoConversazione, max_passaggi: int) -> Literal["strumenti", "fine"]:
    """Decide dove andare dopo il nodo llm."""
    if not _richieste_di_tool(stato):
        log.info("Instradamento: risposta finale → fine")
        return "fine"
    if stato.get("passaggi", 0) >= max_passaggi:
        log.info("Instradamento: strumento richiesto ma limite di passaggi raggiunto → fine")
        return "fine"
    log.info("Instradamento: il modello chiede uno strumento → strumenti")
    return "strumenti"


def _esegui_richiesta(richiesta: dict, per_nome: dict[str, BaseTool]) -> str:
    strumento = per_nome.get(richiesta["name"])
    if strumento is None:
        return f"Errore: strumento sconosciuto {richiesta['name']!r}. Disponibili: {', '.join(per_nome) or 'nessuno'}."
    inattesi = set(richiesta["args"]) - set(strumento.args)
    if inattesi:
        return (
            f"Errore: argomenti non previsti per {strumento.name}: {', '.join(sorted(inattesi))}. "
            f"Argomenti ammessi: {', '.join(strumento.args) or 'nessuno'}."
        )
    try:
        return str(strumento.invoke(richiesta["args"]))
    except Exception as errore:
        return f"Errore: {strumento.name} non è riuscito: {errore}"


def crea_grafo(
    modello: Runnable, strumenti: Sequence[BaseTool] = (), max_passaggi: int = 6
) -> CompiledStateGraph:
    per_nome = {strumento.name: strumento for strumento in strumenti}

    def llm(stato: StatoConversazione) -> dict:
        passaggi = stato.get("passaggi", 0) + 1
        log.info("Inizio chiamata al modello (passaggio %d, %d messaggi)", passaggi, len(stato["messages"]))
        inizio = time.perf_counter()
        risposta = modello.invoke([SystemMessage(PROMPT_SISTEMA), *stato["messages"]])
        log.info("Fine chiamata al modello in %.2f s", time.perf_counter() - inizio)
        aggiornamento = {"messages": [risposta], "passaggi": passaggi}
        if getattr(risposta, "tool_calls", None) and passaggi >= max_passaggi:
            log.warning("Limite di %d passaggi raggiunto: turno interrotto senza risposta finale", max_passaggi)
            aggiornamento["limite_raggiunto"] = True
        return aggiornamento

    def nodo_strumenti(stato: StatoConversazione) -> dict:
        risposte = []
        for richiesta in _richieste_di_tool(stato):
            log.info("Richiesta di strumento: %s(%s)", richiesta["name"], richiesta["args"])
            risultato = _esegui_richiesta(richiesta, per_nome)
            log.info("Risultato di %s: %s", richiesta["name"], risultato)
            risposte.append(ToolMessage(risultato, tool_call_id=richiesta["id"], name=richiesta["name"]))
        return {"messages": risposte}

    costruttore = StateGraph(StatoConversazione)
    costruttore.add_node("llm", llm)
    costruttore.add_node("strumenti", nodo_strumenti)
    costruttore.add_edge(START, "llm")
    costruttore.add_conditional_edges(
        "llm", lambda stato: instrada(stato, max_passaggi), {"strumenti": "strumenti", "fine": END}
    )
    costruttore.add_edge("strumenti", "llm")
    return costruttore.compile()
