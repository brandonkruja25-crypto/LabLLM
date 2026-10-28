"""Modelli finti per i test: nessuna chiamata a LM Studio."""

from datetime import datetime, timezone

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

ISTANTE_INVERNO = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
TOKYO_INVERNO = "2026-01-15T21:00:00+09:00 (Asia/Tokyo)"


def modello_a_copione(*passi):
    """Modello finto: ogni passo è un AIMessage da restituire o un'eccezione da sollevare."""
    coda = list(passi)

    def rispondi(messaggi):
        passo = coda.pop(0)
        if isinstance(passo, Exception):
            raise passo
        return passo

    return RunnableLambda(rispondi)


def richiesta_strumento(nome="ora_corrente", argomenti=None, id_chiamata="call_1"):
    if argomenti is None:
        argomenti = {"fuso_orario": "Asia/Tokyo"}
    return AIMessage("", tool_calls=[{"name": nome, "args": argomenti, "id": id_chiamata}])
