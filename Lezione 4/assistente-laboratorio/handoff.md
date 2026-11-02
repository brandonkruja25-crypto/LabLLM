# Handoff — assistente del laboratorio

Aggiornato: 2026-11-02 · Branch: `main` · Push su `origin/main` eseguito su richiesta dell'utente

## Stato

Piano `docs/superpowers/plans/2026-10-27-assistente-laboratorio.md` eseguito per intero (Task 1–7),
seguito da una revisione indipendente di tutto il lavoro e dalle correzioni che ne sono uscite.
Struttura e comandi sono in `CLAUDE.md`; configurazione, avvio e diagnosi nel README.

| Verifica | Esito |
|---|---|
| `python -m pytest` | 70 passed, 4 deselected |
| `python -m pytest -m lmstudio -v` | 3 passed (due turni con cronologia, ora a Tokyo con lo strumento, domanda ordinaria senza strumento) |
| `docker compose build` + `python -m pytest -m docker -v` | 1 passed (riga `[strumento]` con `Asia/Tokyo` e risposta che usa l'ora) |
| Chat locale con `LIVELLO_LOG=INFO` | traccia completa: chiamata al modello, instradamento, richiesta, risultato, risposta |
| `docker ps`, `docker logs -f assistente-demo` | container senza porte; log visibili; fuso del container (UTC) ininfluente |
| Chat Docker con TTY, digitando a mano | funziona (confermato dall'utente) |

## Da verificare ancora

- LM Studio spento davvero (provato con una porta chiusa) e Ctrl+C in una chat interattiva
  (coperto dai test automatici).

## Decisioni prese con l'utente durante l'esecuzione

- `fuso_orario` descritto nello schema dello strumento e nel prompt di sistema: con
  `google/gemma-4-e2b` la prova sull'ora a Tokyo è passata da 12 su 17 a 12 su 12.
- Giorno della settimana nel risultato dello strumento (specifica 6.3 e RF-06 aggiornati): senza,
  il modello lo calcolava e a volte sbagliava.

## Scelte del costruttore

- Il nodo `strumenti` rifiuta gli argomenti non previsti (pydantic li ignorerebbe) e restituisce un
  errore anche per gli argomenti non in JSON valido (`invalid_tool_calls`).
- `main` carica `.env` solo senza ambiente esplicito; gestisce Ctrl+C all'avvio (codice 130) e
  l'output rediretto su Windows senza traceback; `LMSTUDIO_BASE_URL` viene validato.
- I test di rollback per errore di connessione e HTTP sono un unico test parametrizzato.
- Il terminale ignora il BOM che PowerShell antepone all'input passato con una pipe (senza, «esci»
  da pipe non chiudeva la chat).

## Altri documenti

- `AVVIO.md`: guida passo per passo per avviare il programma fino alla chat.
- `docs/esposizione/`: guida PDF completa e promemoria di 5 pagine per l'esposizione, con gli
  script che li generano (istruzioni in testa a ciascuno script).

## Limiti noti rimandati

- La prova Docker non ricostruisce l'immagine: eseguire prima `docker compose build`.
- Una risposta del modello fatta di soli spazi stampa `Assistente> ` vuoto invece del testo
  «(il modello non ha restituito testo)».
- Il modello resta non deterministico: un fallimento occasionale della prova reale va segnalato.
