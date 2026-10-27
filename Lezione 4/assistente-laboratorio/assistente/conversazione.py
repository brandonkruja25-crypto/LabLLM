"""Cronologia della sessione: ogni turno passa dal grafo e viene conservato solo se riesce."""

import logging
from dataclasses import dataclass, field

import openai
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

log = logging.getLogger(__name__)


class ErroreModello(Exception):
    """Il modello non è raggiungibile o ha risposto con un errore."""


@dataclass
class ChiamataStrumento:
    nome: str
    argomenti: dict
    risultato: str


@dataclass
class EsitoTurno:
    risposta: str | None
    chiamate: list[ChiamataStrumento] = field(default_factory=list)
    limite_raggiunto: bool = False


class Conversazione:
    def __init__(self, grafo: CompiledStateGraph, base_url: str):
        self.grafo = grafo
        self.base_url = base_url
        self.cronologia: list[BaseMessage] = []

    def invia(self, testo: str) -> EsitoTurno:
        ingresso = {"messages": [*self.cronologia, HumanMessage(testo)]}
        try:
            risultato = self.grafo.invoke(ingresso)
        except openai.APIError as errore:
            log.error("Chiamata al modello fallita: %s", errore)
            raise ErroreModello(
                f"Impossibile contattare il modello su {self.base_url}: {str(errore).rstrip('.')}. "
                "Controlla che LM Studio sia avviato, che il server sia attivo "
                "e che LMSTUDIO_BASE_URL sia corretto."
            ) from errore

        messaggi = risultato["messages"]
        self.cronologia = list(messaggi)
        ultimo = messaggi[-1]
        risposta = ultimo.text if isinstance(ultimo, AIMessage) else None
        return EsitoTurno(risposta)
