"""Interfaccia da terminale: legge le domande, mostra chiamate agli strumenti e risposte."""

import json
from collections.abc import Callable

from assistente.conversazione import ChiamataStrumento, ErroreModello

COMANDO_USCITA = "esci"


def formatta_chiamata(chiamata: ChiamataStrumento) -> str:
    argomenti = ", ".join(
        f"{nome}={json.dumps(valore, ensure_ascii=False)}" for nome, valore in chiamata.argomenti.items()
    )
    return f"[strumento] {chiamata.nome}({argomenti}) → {chiamata.risultato}"


def esegui_chat(conversazione, leggi: Callable[[str], str] = input, scrivi: Callable[[str], None] = print) -> None:
    """Ciclo della chat; termina con «esci», Ctrl+C o fine input, senza traceback."""
    try:
        while True:
            try:
                # Il BOM (U+FEFF) arriva quando PowerShell passa l'input con una pipe.
                testo = leggi("Tu> ").lstrip("﻿").strip()
            except EOFError:
                scrivi("")
                return
            if not testo:
                continue
            if testo.lower() == COMANDO_USCITA:
                return

            try:
                esito = conversazione.invia(testo)
            except ErroreModello as errore:
                scrivi(f"Errore: {errore}")
                continue

            for chiamata in esito.chiamate:
                scrivi(formatta_chiamata(chiamata))
            if esito.limite_raggiunto:
                scrivi("Limite di passaggi raggiunto: nessuna risposta finale. Riformula la domanda.")
            elif esito.risposta:
                scrivi(f"Assistente> {esito.risposta}")
            else:
                scrivi("Assistente> (il modello non ha restituito testo)")
    except KeyboardInterrupt:
        scrivi("")
