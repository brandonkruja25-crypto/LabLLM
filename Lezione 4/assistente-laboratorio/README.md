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
