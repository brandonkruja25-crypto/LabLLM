# Assistente del laboratorio

Chat da terminale in Python che conversa con un modello locale servito da LM Studio. Il flusso è
organizzato in un grafo LangGraph esplicito. Progetto della Lezione 4 del corso «Deep Learning e
LLM: costruire chatbot e agenti».

## Requisiti

- Python 3.13
- LM Studio sull'host, con il server API attivo
- Docker Desktop (solo per l'avvio con Docker Compose)

## Ambiente (PowerShell)

Dalla cartella `assistente-laboratorio`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Configurazione

La configurazione arriva solo da variabili d'ambiente; in locale si usa un file `.env`
(escluso da Git) creato dall'esempio:

```powershell
Copy-Item .env.example .env
```

| Variabile | Obbligatoria | Default | Note |
|---|---|---|---|
| `LMSTUDIO_BASE_URL` | sì | — | Indirizzo del server di LM Studio, es. `http://localhost:1234/v1` |
| `LMSTUDIO_MODEL` | sì | — | Identificativo restituito da `GET /v1/models` |
| `FUSO_ORARIO_PREDEFINITO` | no | `Europe/Rome` | Nome di fuso IANA |
| `MAX_PASSAGGI` | no | `6` | Intero ≥ 1 |
| `LIVELLO_LOG` | no | `WARNING` | `DEBUG`, `INFO`, `WARNING` o `ERROR` |

Per conoscere gli identificativi dei modelli disponibili, con il server di LM Studio attivo:

```powershell
Invoke-RestMethod http://localhost:1234/v1/models | Select-Object -ExpandProperty data | Select-Object id
```

LM Studio non richiede una chiave API: il programma usa un valore segnaposto fisso.

## Avvio locale

Con l'ambiente attivo e LM Studio avviato:

```powershell
python -m assistente
```

Si scrive dopo `Tu> `; la risposta arriva dopo `Assistente> `. Per uscire: `esci`, Ctrl+C o fine
input. La cronologia vale per la sola sessione.

All'avvio il programma controlla il modello con `GET /v1/models`:

- server che non risponde: avviso, la chat si apre e ogni domanda mostra un errore con
  l'indirizzo provato finché LM Studio non è raggiungibile;
- modello assente dall'elenco: il programma termina mostrando gli identificativi disponibili.

### Log

I log vanno su standard error e sono silenziosi di default. Per vedere inizio, fine e durata
delle chiamate al modello:

```powershell
$env:LIVELLO_LOG="INFO"
python -m assistente
```

A livello `INFO` i log compaiono nello stesso terminale della chat.

## Strumento orologio

Il modello può chiedere lo strumento `ora_corrente`. Il programma lo esegue davvero e restituisce al
modello il risultato.

| Parte | Contratto |
|---|---|
| Parametro | `fuso_orario`, facoltativo: nome di fuso IANA (`Europe/Rome`, `Asia/Tokyo`, `America/New_York`, `UTC`) |
| Senza parametro | si usa `FUSO_ORARIO_PREDEFINITO` |
| Risultato | `AAAA-MM-GGTHH:MM:SS±HH:MM (Nome/IANA), giorno`, calcolato da UTC: il fuso del computer o del container non conta. Il giorno della settimana è quello del fuso richiesto, in italiano |
| Fuso non valido | testo che inizia con `Errore:` restituito al modello, nessuna eccezione |

Ogni chiamata compare nella chat prima della risposta:

```
Tu> Che ore sono adesso a Tokyo?
[strumento] ora_corrente(fuso_orario="Asia/Tokyo") → 2026-10-28T20:08:51+09:00 (Asia/Tokyo), mercoledì
Assistente> Adesso sono le 20:08:51 di mercoledì 28 ottobre 2026 a Tokyo.
```

Il grafo è `START → llm → (strumenti → llm)* → END`. Il ciclo si ferma dopo `MAX_PASSAGGI` chiamate
al modello. In quel caso la chat mostra `Limite di passaggi raggiunto` invece di una risposta, e la
cronologia torna com'era prima della domanda.

Con `$env:LIVELLO_LOG="INFO"` i log mostrano, per ogni turno, la chiamata al modello, la decisione
di instradamento, la richiesta dello strumento con gli argomenti e il risultato.

La prova reale `-m lmstudio` dimostra che il modello locale chiede davvero lo strumento: per una
domanda sull'ora a Tokyo serve almeno una chiamata con `fuso_orario` uguale a `Asia/Tokyo`, la
risposta deve contenere l'ora restituita e una domanda ordinaria non deve usare lo strumento.
Con `google/gemma-4-e2b` il modello a volte ometteva `fuso_orario` (5 casi su 17). Dopo aver
aggiunto la descrizione del parametro e un'indicazione nel prompt di sistema, la prova è passata
12 volte su 12. Il modello resta non deterministico: un errore occasionale va segnalato, non
nascosto. Il risultato comprende anche il giorno della settimana: prima il modello lo calcolava da
sé e a volte sbagliava (ad esempio «lunedì» per mercoledì 28 ottobre 2026).

## Docker Compose

Nel container gira solo l'applicazione. LM Studio resta sull'host e il container lo raggiunge su
`http://host.docker.internal:1234/v1`: `compose.yaml` imposta questo indirizzo, che prevale su
quello del `.env`. Le altre variabili arrivano dal `.env`. Non viene pubblicata nessuna porta.

```powershell
docker compose build
docker compose run --rm --name assistente-demo assistente
```

Da un secondo terminale, mentre la chat è aperta:

```powershell
docker ps
docker logs -f assistente-demo
```

Per vedere nei log le chiamate al modello e allo strumento, impostare `LIVELLO_LOG=INFO` nel `.env`
oppure passarlo solo per quell'avvio:

```powershell
docker compose run --rm --name assistente-demo -e LIVELLO_LOG=INFO assistente
```

A livello `INFO` i log compaiono sia in `docker logs -f` sia nel terminale della chat, perché con
la TTY stdout e stderr condividono lo stesso flusso. I log del container sono in UTC, ma l'ora
restituita dallo strumento dipende solo dal fuso richiesto.

Prova automatica dal container: chiede l'ora a Tokyo con input da pipe (`-T`) e controlla la
riga `[strumento]`. Richiede Docker, il file `.env` e LM Studio attivo.

```powershell
python -m pytest -m docker -v
```

> Verifica: build, `docker ps`, `docker logs -f` e la prova `-m docker` sono stati eseguiti con
> esito positivo. La chat interattiva con TTY (`docker compose run --rm --name assistente-demo
> assistente` digitando a mano) è ancora da confermare in un terminale interattivo.

### Diagnosi

| Sintomo | Cause probabili | Cosa controllare |
|---|---|---|
| Compose non parte: `env file ... .env not found` | Manca il file `.env` | `Copy-Item .env.example .env` |
| Il container termina subito con `Errore di configurazione: ...` | Una variabile mancante o non valida, nominata nel messaggio | Correggere quella variabile nel `.env` |
| Avviso «il server ... non risponde» e `Errore: Impossibile contattare il modello` | LM Studio spento, server API non avviato, o server in ascolto solo sull'interfaccia locale | In LM Studio avviare il server; se il container non lo raggiunge, attivare l'opzione per servire sulla rete locale e controllare il firewall di Windows per la porta 1234 |
| Il programma termina con «non è tra i modelli» | `LMSTUDIO_MODEL` diverso dagli identificativi del server | Usare un id dall'elenco mostrato, o da `Invoke-RestMethod http://localhost:1234/v1/models` |
| La risposta sull'ora non ha la riga `[strumento]` | Il modello ha risposto senza chiedere lo strumento | Avviare con `LIVELLO_LOG=INFO` e leggere instradamento e richieste; riformulare la domanda; segnalare il caso come limite del modello |

In questo ambiente (Docker Desktop su Windows) il container ha raggiunto LM Studio senza
modifiche alla rete o al firewall.

## Test

```powershell
python -m pytest
```

I test automatici non richiedono un modello attivo. Le prove reali sono escluse di default e si
attivano esplicitamente:

```powershell
python -m pytest -m lmstudio -v
```

Richiedono il file `.env` e LM Studio con il server attivo.
