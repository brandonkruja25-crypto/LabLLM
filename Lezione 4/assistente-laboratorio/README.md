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

## Test

```powershell
python -m pytest
```

I test automatici non richiedono un modello attivo.
