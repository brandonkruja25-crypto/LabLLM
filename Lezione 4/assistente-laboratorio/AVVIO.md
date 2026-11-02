# Come avviare l'assistente del laboratorio

Guida passo per passo, dall'accensione fino alla chat. Tutti i comandi vanno scritti in
**PowerShell**.

Ci sono due modi per avviare il programma. Scegline uno:

- **Modo A, in locale:** il programma gira direttamente con Python sul tuo PC.
- **Modo B, con Docker:** il programma gira in un container.

In entrambi i casi il modello resta in **LM Studio**, sul tuo PC.

---

## Passo 1 · Avvia LM Studio

1. Apri **LM Studio**.
2. Carica il modello **google/gemma-4-e2b**.
3. Avvia il **server locale** di LM Studio, che di solito ascolta sulla porta `1234`.
4. Controlla che il server risponda:

   ```powershell
   Invoke-RestMethod http://localhost:1234/v1/models | Select-Object -ExpandProperty data | Select-Object id
   ```

   Nell'elenco deve comparire `google/gemma-4-e2b`. Se compare un errore, il server non è attivo.

> Tieni LM Studio aperto per tutto il tempo in cui usi la chat.

---

## Passo 2 · Apri la cartella del progetto

```powershell
cd "C:\Users\KBrandon\Desktop\LLM\Lezione 4\assistente-laboratorio"
```

---

## Passo 3 · Prepara la configurazione (solo la prima volta)

Il programma legge le impostazioni dal file `.env`. Se il file non c'è ancora, crealo dall'esempio:

```powershell
Copy-Item .env.example .env
```

Non serve modificarlo: contiene già l'indirizzo di LM Studio e il nome del modello.

---

## Modo A · Avvio in locale

### A1 · Prepara Python (solo la prima volta)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

### A2 · Attiva l'ambiente (ogni volta che apri un nuovo terminale)

```powershell
.\.venv\Scripts\Activate.ps1
```

All'inizio della riga del terminale compare `(.venv)`.

### A3 · Avvia la chat

```powershell
python -m assistente
```

Per vedere anche cosa succede dietro le quinte (chiamate al modello e allo strumento):

```powershell
$env:LIVELLO_LOG="INFO"
python -m assistente
```

Poi vai al passo **«La chat»** più sotto.

---

## Modo B · Avvio con Docker

Serve **Docker Desktop** avviato.

### B1 · Costruisci l'immagine (la prima volta e dopo ogni modifica al codice)

```powershell
docker compose build
```

### B2 · Avvia la chat nel container

```powershell
docker compose run --rm --name assistente-demo assistente
```

Per vedere anche i log delle chiamate:

```powershell
docker compose run --rm --name assistente-demo -e LIVELLO_LOG=INFO assistente
```

### B3 · Controlla il container (facoltativo)

Da un **secondo terminale**, mentre la chat è aperta:

```powershell
docker ps
docker logs -f assistente-demo
```

Poi vai al passo **«La chat»** qui sotto.

---

## La chat

All'avvio compare:

```
Assistente del laboratorio — modello google/gemma-4-e2b su http://localhost:1234/v1
Scrivi «esci» per terminare.
Tu>
```

Con Docker l'indirizzo mostrato è `http://host.docker.internal:1234/v1`: è normale.

Scrivi la domanda dopo `Tu>` e premi Invio. Per esempio:

```
Tu> Che ore sono adesso a Tokyo?
[strumento] ora_corrente(fuso_orario="Asia/Tokyo") → 2026-10-28T20:08:51+09:00 (Asia/Tokyo), mercoledì
Assistente> Adesso sono le 20:08:51 di mercoledì 28 ottobre 2026 a Tokyo.
```

- La riga `[strumento]` mostra che il programma ha davvero letto l'orologio.
- Ogni risposta richiede alcuni secondi: il modello «ragiona» prima di rispondere.
- L'assistente ricorda la conversazione finché la chat resta aperta.

**Per uscire:** scrivi `esci`, oppure premi `Ctrl+C`.

---

## Se qualcosa non va

| Cosa vedi | Cosa fare |
|---|---|
| `Avviso: il server su ... non risponde` | LM Studio è chiuso o il server non è avviato: rifai il Passo 1. |
| `Errore: Impossibile contattare il modello su ...` | Come sopra; la chat resta aperta, puoi riprovare dopo aver avviato il server. |
| `... non è tra i modelli di ...` | Il modello indicato nel `.env` non è caricato in LM Studio: carica `google/gemma-4-e2b`. |
| `Errore di configurazione: ...` | Il messaggio indica quale variabile del `.env` correggere. |
| `env file ... .env not found` (Docker) | Manca il file `.env`: rifai il Passo 3. |
| PowerShell non esegue `Activate.ps1` | Avvia senza attivare l'ambiente: `.\.venv\Scripts\python.exe -m assistente` |

Per altri dettagli (test, diagnosi, configurazione) vedi il `README.md`.
