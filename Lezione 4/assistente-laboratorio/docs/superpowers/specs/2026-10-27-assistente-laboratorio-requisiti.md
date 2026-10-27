# Assistente del laboratorio — requisiti (Lezione 4)

Data: 2026-10-27 · Stato: in attesa di approvazione

Elenco verificabile dei requisiti. Il comportamento dettagliato è nella specifica
[`2026-10-27-assistente-laboratorio-design.md`](2026-10-27-assistente-laboratorio-design.md);
le fonti sono il PDF della Lezione 4 (slide indicate) e `CLAUDE.md`.

Tipo di verifica: **A** = test automatico senza modello · **L** = prova reale con LM Studio ·
**D** = prova reale con Docker · **R** = revisione di file o repository.

## Requisiti funzionali

| ID | Requisito | Fonte | Verifica |
|---|---|---|---|
| RF-01 | Chat da terminale: prompt `Tu> `, risposta `Assistente> `, uscita con `esci`, Ctrl+C o fine input senza traceback; righe vuote ignorate. | slide 7, 22 | A, L |
| RF-02 | Il flusso passa da un grafo LangGraph esplicito: stato con messaggi (`add_messages`), nodo `llm`, nodo `strumenti`, funzione di instradamento scritta nel progetto. | slide 3-6, 12, 22 | A, R |
| RF-03 | Primo incremento: grafo senza LLM che restituisce la risposta fissa «Il grafo è in esecuzione.». | slide 5, 23 | A |
| RF-04 | Il nodo `llm` interroga il modello di LM Studio tramite l'API compatibile con OpenAI, con indirizzo e modello da variabili d'ambiente. | slide 7, CLAUDE.md | A, L |
| RF-05 | Cronologia di sessione: dopo due turni contiene le 2 domande e le 2 risposte, senza duplicati; persa alla chiusura. | slide 8, 22 | A, L |
| RF-06 | Strumento `ora_corrente(fuso_orario?)`: data e ora ISO 8601 con offset e nome del fuso IANA; default da `FUSO_ORARIO_PREDEFINITO`; ora calcolata da UTC, indipendente dal fuso del container. | slide 10-11 | A |
| RF-07 | Fuso non valido: nessuna eccezione, errore testuale restituito al modello con indicazione del formato IANA. | slide 11 | A |
| RF-08 | Ciclo con strumenti: se la risposta contiene richieste di tool, il nodo `strumenti` esegue la funzione reale, aggiunge un `ToolMessage` con il `tool_call_id` corretto e torna a `llm`; altrimenti END. | slide 12 | A, L |
| RF-09 | Limite di passaggi (`MAX_PASSAGGI`, default 6): al raggiungimento il turno termina con un messaggio esplicito, senza risposta inventata. | slide 12, 22 | A |
| RF-10 | Ogni chiamata allo strumento è mostrata in chat (`[strumento] nome(argomenti) → risultato`). | decisione utente | A, L |
| RF-11 | Log su stderr, livello da `LIVELLO_LOG` (default `WARNING`); a INFO: inizio/fine chiamata al modello, instradamento, richiesta e risultato del tool, limite raggiunto. | slide 9, 13, 22 | A, L |
| RF-12 | Server non raggiungibile: errore riconoscibile con indirizzo e suggerimento, sessione aperta, nessuna risposta inventata; cronologia riportata a com'era prima del turno. | slide 9 | A, L |
| RF-13 | Configurazione mancante o non valida: arresto all'avvio con messaggio che nomina la variabile. Modello configurato assente da `GET /v1/models`: arresto con elenco dei modelli disponibili. | CLAUDE.md | A, L |

## Requisiti di esecuzione e ambiente

| ID | Requisito | Fonte | Verifica |
|---|---|---|---|
| RE-01 | `Dockerfile`, `compose.yaml` (servizio `assistente`) e `.dockerignore`; avvio con `docker compose run --rm --name assistente-demo assistente`. | slide 14-17 | D |
| RE-02 | Dal container LM Studio è raggiunto su `http://host.docker.internal:1234/v1`; LM Studio non è containerizzato; nessuna porta pubblicata. | slide 16 | D |
| RE-03 | Nel container il fuso non è dedotto dall'host; `tzdata` incluso. | slide 10 | A, D |
| RE-04 | Python 3.13, codice sincrono, moduli piccoli: grafo, collegamento al modello, strumenti, interfaccia separati. | CLAUDE.md | R |
| RE-05 | Dipendenze motivate con versioni fissate. | CLAUDE.md | R |
| RE-06 | `.env.example` senza credenziali; `.env`, ambienti virtuali e cache esclusi da Git. | CLAUDE.md | R |

## Requisiti di verifica, documentazione e consegna

| ID | Requisito | Fonte | Verifica |
|---|---|---|---|
| RV-01 | Test automatici ripetibili senza modello: grafo, cronologia, instradamento, limite, rollback, strumento con istante controllato, configurazione. | slide 24, CLAUDE.md | A |
| RV-02 | Prove reali con LM Studio e Docker separate dai test automatici e attivate esplicitamente (marcatori `pytest`). | slide 23, 25 | R |
| RV-03 | Prova reale: una domanda sull'ora produce nella traccia richiesta del modello, esecuzione, risultato e risposta che usa il dato; una domanda ordinaria non usa il tool. | slide 13, 25 | L, D |
| RV-04 | README con configurazione, avvio (anche PowerShell), test e diagnosi, con soli comandi verificati. | slide 25, CLAUDE.md | R |
| RV-05 | Specifica e piano in `docs/superpowers/`; `CLAUDE.md` dedicato dentro `assistente-laboratorio/`. | slide 18-19, 21 | R |
| RV-06 | Commit Conventional in italiano, uno per incremento verificato; push eseguito dallo studente; resoconto con commit raggiunto e problemi aperti. | slide 18, 26 | R |

## Fuori ambito

Persistenza della cronologia, altri strumenti, MCP, workflow, RAG, interfacce grafiche o web,
servizi cloud, LM Studio in container, streaming della risposta.
