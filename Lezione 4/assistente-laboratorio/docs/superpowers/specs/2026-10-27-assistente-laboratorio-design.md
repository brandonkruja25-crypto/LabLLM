# Assistente del laboratorio — specifica (Lezione 4)

Data: 2026-10-27 · Stato: in attesa di approvazione

## 1. Scopo e motivazione

Applicazione da terminale in Python che conversa con un modello locale servito da LM Studio,
con il flusso organizzato in un grafo LangGraph esplicito e uno strumento orologio richiesto dal
modello tramite tool calling ed eseguito davvero dal programma.

È il requisito obbligatorio della Lezione 4 del corso «Deep Learning e LLM: costruire chatbot e
agenti» e la base delle lezioni successive (altri strumenti, MCP, workflow, RAG): quelle
estenderanno questo codice e questo grafo, senza ripartire da zero. Per questo contano struttura
leggibile e punti di estensione chiari più delle funzionalità aggiuntive.

## 2. Obiettivi

1. Chat da terminale su più turni, con cronologia conservata per la durata della sessione.
2. Grafo LangGraph esplicito: stato, nodi e instradamento riconoscibili nel codice.
3. Strumento orologio con fuso orario esplicito, richiesto dal modello ed eseguito dal programma;
   chiamata visibile nella chat e nei log.
4. Avvio anche con Docker Compose; LM Studio resta sull'host.
5. Test automatici ripetibili senza modello; prove reali con LM Studio e Docker separate e
   attivate esplicitamente.
6. README con configurazione, avvio, test e diagnosi, con soli comandi verificati (anche PowerShell).

## 3. Non obiettivi

- Persistenza della cronologia tra sessioni.
- Altri strumenti, MCP, workflow, RAG, interfacce grafiche o web, servizi cloud.
- Containerizzare LM Studio.
- Streaming token per token della risposta.

## 4. Anti-obiettivi (sarebbe un fallimento anche se «funziona»)

- Una risposta sull'ora prodotta dal modello senza una chiamata reale allo strumento,
  oppure dichiarare funzionante il tool sulla base di sole risposte simulate.
- Un'eccezione Python a schermo per un errore prevedibile (server spento, fuso non valido,
  modello inesistente).
- L'applicazione che inventa una risposta quando il modello non è raggiungibile o il limite di
  passaggi è stato superato.
- Un fuso orario dedotto implicitamente dal container o dall'host.
- Un identificativo di modello scritto nel codice o inventato.

## 5. Vincoli

- Python 3.13 (versione presente sull'host), codice sincrono, moduli piccoli.
- Lavoro solo dentro `Lezione 4/assistente-laboratorio/`; nessuna modifica ad altre lezioni.
- Configurazione solo da variabili d'ambiente; un `.env.example` senza credenziali; `.env` fuori
  da Git.
- Dipendenze motivate e con versioni fissate.
- Commit in Conventional Commits in italiano, sul branch `main`, senza worktree; push solo su
  richiesta dell'utente.
- Ambiente verificato il 2026-10-27: Python 3.13.14, Docker 29.2.0, Docker Compose v5.0.2,
  LM Studio su `http://localhost:1234/v1` con il modello di chat `google/gemma-4-e2b`.

## 6. Comportamento

### 6.1 Sessione da terminale

```
Assistente del laboratorio — modello google/gemma-4-e2b su http://localhost:1234/v1
Scrivi «esci» per terminare.
Tu> che ore sono a Tokyo?
[strumento] ora_corrente(fuso_orario="Asia/Tokyo") → 2026-10-27T23:04:05+09:00 (Asia/Tokyo)
Assistente> A Tokyo sono le 23:04 del 27 ottobre 2026.
Tu> esci
```

- All'avvio: una riga con modello e indirizzo del server, poi il prompt `Tu> `.
- Ogni chiamata allo strumento nel turno appare come riga `[strumento] nome(argomenti) → risultato`
  prima della risposta; se lo strumento ha restituito un errore, la riga mostra l'errore.
- Uscita con `esci`, Ctrl+C, oppure fine input (Ctrl+D / Ctrl+Z+Invio): chiusura pulita senza
  traceback. Righe vuote ignorate.
- La cronologia è persa alla chiusura (decisione dell'utente).

### 6.2 Grafo

Stato: lista di messaggi gestita con il reducer `add_messages` (aggiunge, non sostituisce) più il
contatore dei passaggi del turno.

```
START → llm ──(il messaggio contiene tool_calls?)──sì──→ strumenti ──→ llm
              └──no──→ END
```

- Nodo `llm`: invia al modello l'intera cronologia più la descrizione dello strumento; aggiunge
  la risposta allo stato.
- Funzione di instradamento scritta esplicitamente nel progetto (non il condizionale
  precostruito), così la decisione è leggibile e registrata nei log.
- Nodo `strumenti`: esegue ogni richiesta di tool del messaggio e aggiunge un `ToolMessage`
  associato al `tool_call_id` corretto. Un nome di tool sconosciuto produce un `ToolMessage` di
  errore, non un crash.
- Limite di passaggi: al massimo `MAX_PASSAGGI` (default 6) chiamate al nodo `llm` per turno. Se
  il limite viene raggiunto, il turno termina e la chat mostra un messaggio esplicito («limite di
  passaggi raggiunto, nessuna risposta finale»), senza risposta inventata.
- Prompt di sistema breve: assistente in italiano; per data e ora usare sempre lo strumento.
- Cronologia: lo stato restituito da un turno è l'ingresso del turno successivo. Dopo due turni
  contiene entrambe le domande e le relative risposte (ed eventuali messaggi di tool), senza
  duplicazioni.

### 6.3 Strumento orologio — contratto

| Parte | Decisione |
|---|---|
| Nome | `ora_corrente` |
| Descrizione | Restituisce data e ora attuali. Da usare ogni volta che servono data o ora correnti, senza inventarle. Il parametro è un nome di fuso IANA, con esempi espliciti: `Europe/Rome`, `Asia/Tokyo`, `America/New_York`, `UTC`. |
| Parametri | `fuso_orario` (stringa, facoltativo). Se assente: valore di `FUSO_ORARIO_PREDEFINITO`. |
| Risultato | ISO 8601 al secondo con offset, seguito dal nome del fuso: `2026-10-27T15:04:05+01:00 (Europe/Rome)`. Ora legale gestita da `zoneinfo`. |
| Errori | Fuso non riconosciuto (es. `Tokyo`, `UTC+2`, testo vuoto o casuale): nessuna eccezione; risultato di errore testuale restituito al modello, con il valore ricevuto e l'indicazione di usare un nome IANA (con esempio). |

- L'istante si ottiene dall'orologio di sistema in UTC e si converte nel fuso richiesto; il fuso
  del processo/container non influisce.
- La funzione accetta un istante iniettabile (o una sorgente dell'ora) per i test.
- Si include la dipendenza `tzdata` perché l'immagine Docker non garantisce il database dei fusi.

### 6.4 Configurazione

Variabili d'ambiente (esempio in `.env.example`):

| Variabile | Obbligatoria | Default | Note |
|---|---|---|---|
| `LMSTUDIO_BASE_URL` | sì | — | Es. `http://localhost:1234/v1`; in Compose `http://host.docker.internal:1234/v1` |
| `LMSTUDIO_MODEL` | sì | — | Identificativo restituito da `GET /v1/models` |
| `FUSO_ORARIO_PREDEFINITO` | no | `Europe/Rome` | Validato all'avvio |
| `MAX_PASSAGGI` | no | `6` | Intero ≥ 1, validato all'avvio |
| `LIVELLO_LOG` | no | `WARNING` | `DEBUG`/`INFO`/`WARNING`/`ERROR` |

- Configurazione non valida o mancante: l'app si ferma all'avvio con un messaggio chiaro che
  nomina la variabile, senza traceback.
- All'avvio l'app interroga `GET /v1/models`: se il server non risponde, avvisa e continua (si
  potrà riprovare nella sessione); se risponde ma `LMSTUDIO_MODEL` non è nell'elenco, termina
  mostrando gli identificativi disponibili.
- LM Studio non richiede chiave: il client usa un valore segnaposto fisso nel codice, non una
  credenziale.

### 6.5 Errori durante la conversazione

- Server non raggiungibile o errore HTTP nella chiamata al modello: messaggio chiaro con
  l'indirizzo provato e un suggerimento (LM Studio avviato? server attivo? URL corretto?), la
  sessione resta aperta. Il messaggio dell'utente di quel turno non lascia nella cronologia una
  risposta inventata.
- Nessuna risposta di ripiego generata dall'applicazione.
- Turno fallito o interrotto dal limite di passaggi: la cronologia torna esattamente com'era
  prima del turno (rollback completo: né la domanda, né richieste di tool rimaste senza
  risposta, né risultati parziali). Così la richiesta successiva a LM Studio è sempre valida;
  l'utente può riformulare la domanda.

### 6.6 Log

- Modulo `logging` su standard error (così `docker logs -f` li mostra); livello da `LIVELLO_LOG`,
  silenziosi di default (decisione dell'utente).
- Eventi a livello INFO: inizio e fine della chiamata al modello con durata; decisione di
  instradamento; richiesta di tool con nome e argomenti; risultato del tool; limite di passaggi
  raggiunto. Errori di connessione a livello ERROR/WARNING.
- Con livello `INFO` o `DEBUG` i log compaiono anche nel terminale della chat (sia in locale sia
  nel container con TTY, dove stdout e stderr condividono lo stesso flusso) e in
  `docker logs -f`. È accettato: di default sono silenziosi; il README lo segnala.

### 6.7 Docker

- `Dockerfile` su immagine `python:3.13-slim`, dipendenze da file con versioni fissate.
- `compose.yaml` con servizio `assistente`, `env_file: .env`, `LMSTUDIO_BASE_URL` impostato a
  `http://host.docker.internal:1234/v1`, `stdin_open` e `tty` per la chat. Nessuna porta pubblicata.
- `.dockerignore` che esclude `.env`, ambienti virtuali, cache, `.git`.
- Avvio documentato: `docker compose build` e
  `docker compose run --rm --name assistente-demo assistente`; log con
  `docker logs -f assistente-demo` da un secondo terminale.
- LM Studio deve ascoltare su un indirizzo raggiungibile dal container (opzione di rete locale
  attiva in LM Studio, firewall): da documentare nella diagnosi del README.

## 7. Test e verifiche

### 7.1 Automatici (sempre, senza modello né Docker) — `pytest`

- Strumento con istante controllato: Roma in inverno (+01:00) e in estate (+02:00), Tokyo, UTC,
  default da configurazione, fuso non valido → errore testuale, stringa vuota.
- Grafo con modello finto che restituisce risposte prestabilite:
  - conversazione ordinaria: START → llm → END, nessun tool;
  - richiesta di tool: llm → strumenti → llm → END, `ToolMessage` con `tool_call_id` corretto e
    contenuto prodotto dalla funzione reale;
  - limite di passaggi: modello che chiede sempre il tool → il turno termina al limite.
- Cronologia: due turni consecutivi → 2 domande e 2 risposte, nessun duplicato.
- Rollback: turno con errore del server seguito da un turno normale, e turno interrotto dal
  limite seguito da un turno normale → la cronologia contiene solo i turni riusciti.
- Configurazione: variabili mancanti o non valide → errore chiaro.
- Interfaccia: `esci`, fine input e righe vuote; riga `[strumento]` stampata.

### 7.2 Prove reali (solo su richiesta esplicita)

- Marcatori `pytest` separati (es. `lmstudio`, `docker`), esclusi dall'esecuzione di default.
- Con LM Studio: una domanda ordinaria (nessun tool) e una sull'ora in un fuso diverso; si
  verifica nella traccia che la richiesta di tool sia stata fatta dal modello reale, che la
  funzione sia stata eseguita e che la risposta usi il dato.
- Con Docker: build e avvio via Compose, collegamento dal container a LM Studio, stessa prova
  sull'orologio.
- Una risposta simulata non dimostra che il modello locale sappia usare lo strumento. Se
  `google/gemma-4-e2b` non richiede il tool in modo affidabile, va riportato come problema aperto
  (non mascherato), discutendo con l'utente eventuali alternative.

## 8. Corrispondenza con la consegna (slide 26)

L'elenco completo dei requisiti, con fonte e tipo di verifica, è in
[`2026-10-27-assistente-laboratorio-requisiti.md`](2026-10-27-assistente-laboratorio-requisiti.md).

| Requisito obbligatorio | Evidenza richiesta | Dove nella specifica | Prova che lo dimostra | Requisiti |
|---|---|---|---|---|
| Grafo con LLM e cronologia | Conversazione funzionante su più turni | 6.1, 6.2 | Test grafo e cronologia con modello finto (7.1); conversazione di più turni con LM Studio (7.2) | RF-02…RF-05, RF-12 |
| Strumento orologio | Richiesta, esecuzione e risultato visibili nella traccia | 6.3, 6.1, 6.6 | Test strumento con istante fisso e test del ciclo (7.1); domanda sull'ora con il modello reale, riga `[strumento]` e log INFO (7.2) | RF-06…RF-11 |
| Docker Compose | Applicazione nel container collegata a LM Studio | 6.7 | `docker compose build` + `docker compose run`, stessa prova sull'orologio dal container (7.2) | RE-01…RE-03 |
| Test | Risultati automatici e prove reali distinti | 7.1, 7.2 | `pytest` di default senza modello; prove reali solo con marcatori espliciti | RV-01…RV-03 |
| Documentazione | README, configurazione di esempio e CLAUDE.md coerenti | 6.4, 6.7 | Revisione finale: comandi del README eseguiti davvero, `.env.example` sufficiente, `CLAUDE.md` aggiornato | RV-04, RV-05, RE-06 |
| Repository condivisa | Commit leggibili e push eseguito dallo studente | 5 | `git log` con Conventional Commits; push fatto dall'utente; resoconto con commit raggiunto e problemi aperti | RV-06 |

## 9. Decisioni e scelte del costruttore

Decise con l'utente:
- fuso orario selezionabile dal modello tramite parametro validato, con default da configurazione;
- chiamate allo strumento visibili sia in chat sia nei log;
- log silenziosi di default (`WARNING`), da alzare quando serve;
- cronologia persa alla chiusura;
- repository in `Desktop\LLM`, progetto in `Lezione 4/assistente-laboratorio/`.

Scelte mie (da confermare leggendo):
- collegamento al modello con `langchain-openai` (`ChatOpenAI` con `base_url` di LM Studio e
  `bind_tools`), perché produce messaggi compatibili con lo stato LangGraph; niente SDK
  `openai` usato direttamente;
- `python-dotenv` per caricare `.env` nell'esecuzione locale senza Docker;
- `pytest` per i test; versioni fissate in fase di piano;
- nome dello strumento e del parametro in italiano (`ora_corrente`, `fuso_orario`);
- default `MAX_PASSAGGI=6`;
- controllo del modello via `GET /v1/models` all'avvio;
- rollback completo del turno in caso di errore o di limite di passaggi;
- log a livello INFO mescolati alla chat quando vengono attivati (nessun file di log separato).

Lasciate al costruttore: nomi dei moduli e dei file, formato preciso dei messaggi di errore e
dei log, struttura interna dei test, testo esatto del prompt di sistema.
