# Assistente del laboratorio — piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Obiettivo:** chat da terminale con grafo LangGraph esplicito, modello di LM Studio, cronologia di
sessione, strumento orologio richiesto dal modello ed eseguito dal programma, avvio con Docker Compose.

**Architettura:** pacchetto `assistente/` con moduli piccoli: `configurazione` (variabili d'ambiente),
`strumenti` (orologio), `modello` (client LM Studio), `grafo` (stato, nodi, instradamento),
`conversazione` (cronologia e rollback del turno), `terminale` (I/O), `__main__` (avvio). Il grafo è
compilato senza checkpointer: la cronologia vive in `Conversazione` ed entra nel grafo a ogni turno;
viene aggiornata solo se il turno riesce.

**Tecnologie:** Python 3.13, langgraph 1.2.18, langchain-core 1.7.0, langchain-openai 1.7.3,
openai 3.39.0, python-dotenv 1.2.4, tzdata 2026.5, pytest 9.1.1, Docker Compose v5.

**Specifica:** `docs/superpowers/specs/2026-10-27-assistente-laboratorio-design.md` e
`docs/superpowers/specs/2026-10-27-assistente-laboratorio-requisiti.md` (ID RF/RE/RV citati nei task).

## Vincoli globali

- Tutti i percorsi sono relativi a `Lezione 4/assistente-laboratorio/`; tutti i comandi si eseguono
  da lì in PowerShell, con l'ambiente virtuale `.venv` attivo.
- Solo dipendenze elencate qui, con versioni esatte (`==`). Versioni verificate con
  `pip install --dry-run` il 2026-10-27: si risolvono insieme.
- Codice sincrono; nessuna persistenza; nessun altro strumento, MCP, RAG, interfaccia web.
- Configurazione solo da ambiente: `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL` (obbligatorie),
  `FUSO_ORARIO_PREDEFINITO` (default `Europe/Rome`), `MAX_PASSAGGI` (default `6`, intero ≥ 1),
  `LIVELLO_LOG` (default `WARNING`; `DEBUG`/`INFO`/`WARNING`/`ERROR`).
- Strumento: nome `ora_corrente`, parametro facoltativo `fuso_orario`; risultato
  `AAAA-MM-GGTHH:MM:SS±HH:MM (Nome/IANA)`; errori come testo che inizia con `Errore:`.
- Riga in chat: `[strumento] ora_corrente(fuso_orario="Asia/Tokyo") → <risultato>`; prompt `Tu> `,
  risposte `Assistente> `; uscita con `esci`, Ctrl+C, fine input.
- Chiave API: segnaposto fisso `"lm-studio"` nel codice (LM Studio non la richiede).
- Ogni task termina con test verdi, `git status`, lettura del diff, staging selettivo e commit
  Conventional in italiano con riga `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  Nessun push.
- `python -m pytest` di default esclude le prove reali (marcatori `lmstudio`, `docker`).

## Focus di revisione

Casi che la specifica implica ma che un test diretto non coprirebbe; ciascuno ha un test nel task indicato.

1. Il modello passa `fuso_orario` con spazi (`" Asia/Tokyo "`) o un percorso (`"../etc/passwd"`):
   spazi rimossi; percorso → `Errore:` senza eccezione (Task 4).
2. Il modello chiama lo strumento con argomenti sbagliati (`{"timezone": "Asia/Tokyo"}`) o uno
   strumento inesistente: `ToolMessage` di errore, il turno prosegue (Task 5).
3. LM Studio risponde con errore HTTP (modello scaricato) invece di rifiutare la connessione:
   stesso messaggio chiaro e rollback (Task 2).
4. Il modello restituisce testo vuoto senza tool: la chat mostra
   `Assistente> (il modello non ha restituito testo)` (Task 3).
5. Ctrl+C durante l'attesa della risposta: uscita pulita senza traceback (Task 3).

---

## Incremento 1 — Grafo con risposta fissa

### Task 1: Struttura del progetto e grafo con risposta fissa (RF-03, RE-04, RE-05)

**File:**
- Crea: `requirements.txt`, `requirements-dev.txt`, `pytest.ini`, `.gitignore`, `README.md`
- Crea: `assistente/__init__.py` (vuoto), `assistente/grafo.py`
- Test: `tests/__init__.py` (vuoto), `tests/test_grafo.py`

**Interfacce:**
- Produce: `StatoConversazione` (TypedDict: `messages: Annotated[list[AnyMessage], add_messages]`),
  `crea_grafo_fisso() -> CompiledStateGraph`, costante `RISPOSTA_FISSA = "Il grafo è in esecuzione."`.

- [ ] **Passo 1: file di progetto**
  - `requirements.txt`: `langgraph==1.2.18`, `langchain-core==1.7.0`, `langchain-openai==1.7.3`,
    `openai==3.39.0`, `python-dotenv==1.2.4`, `tzdata==2026.5`, ciascuno con un commento di una
    riga che ne motiva la presenza.
  - `requirements-dev.txt`: `-r requirements.txt` e `pytest==9.1.1`.
  - `pytest.ini`: `testpaths = tests`, `pythonpath = .`,
    `addopts = -m "not lmstudio and not docker"`, marcatori `lmstudio` e `docker` descritti.
  - `.gitignore`: `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`.
- [ ] **Passo 2: ambiente**
  Run: `python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install -r requirements-dev.txt`
  Atteso: installazione senza errori; `python -m pip show langgraph` mostra `1.2.18`.
- [ ] **Passo 3: test che falliscono** in `tests/test_grafo.py`

```python
from langchain_core.messages import AIMessage, HumanMessage
from assistente.grafo import RISPOSTA_FISSA, crea_grafo_fisso

def test_grafo_fisso_aggiunge_la_risposta_prevista():
    risultato = crea_grafo_fisso().invoke({"messages": [HumanMessage("ciao")]})
    assert [type(m) for m in risultato["messages"]] == [HumanMessage, AIMessage]
    assert risultato["messages"][-1].content == RISPOSTA_FISSA == "Il grafo è in esecuzione."

def test_grafo_fisso_esegue_il_nodo_una_volta():
    passi = list(crea_grafo_fisso().stream({"messages": [HumanMessage("x")]}, stream_mode="updates"))
    assert [list(p) for p in passi] == [["risposta"]]
```

- [ ] **Passo 4:** `python -m pytest tests/test_grafo.py -v` → FAIL (`ModuleNotFoundError`).
- [ ] **Passo 5: implementa** in `assistente/grafo.py` lo stato e `crea_grafo_fisso()`: un nodo
  `"risposta"` che restituisce `{"messages": [AIMessage(RISPOSTA_FISSA)]}`; archi
  `START → risposta → END`; `compile()`.
- [ ] **Passo 6:** `python -m pytest -v` → 2 passed.
- [ ] **Passo 7: README** iniziale: scopo, requisiti (Python 3.13, LM Studio, Docker Desktop),
  creazione dell'ambiente (comandi del Passo 2), `python -m pytest`.
- [ ] **Passo 8: commit** — `git add requirements.txt requirements-dev.txt pytest.ini .gitignore README.md assistente tests`
  → `feat(grafo): aggiungi la struttura del progetto e il grafo con risposta fissa`

---

## Incremento 2 — Collegamento a LM Studio e cronologia

### Task 2: Configurazione, client del modello e conversazione con cronologia (RF-04, RF-05, RF-12, RF-13, RE-06)

**File:**
- Crea: `assistente/configurazione.py`, `assistente/modello.py`, `assistente/conversazione.py`, `.env.example`
- Modifica: `assistente/grafo.py` (sostituisce `crea_grafo_fisso` con `crea_grafo`)
- Test: `tests/test_configurazione.py`, `tests/test_modello.py`, `tests/test_conversazione.py`, `tests/test_grafo.py`

**Interfacce:**
- Produce in `configurazione.py`: `class ErroreConfigurazione(Exception)`;
  `@dataclass(frozen=True) class Configurazione(base_url: str, modello: str, fuso_predefinito: str, max_passaggi: int, livello_log: str)`;
  `carica_configurazione(ambiente: Mapping[str, str]) -> Configurazione`.
- Produce in `modello.py`: `CHIAVE_SEGNAPOSTO = "lm-studio"`;
  `crea_modello(config: Configurazione, strumenti: Sequence[BaseTool] = ()) -> Runnable`
  (`ChatOpenAI(base_url=..., model=..., api_key=CHIAVE_SEGNAPOSTO)`, con `.bind_tools(strumenti)` se non vuoto);
  `elenca_modelli(base_url: str, timeout: float = 5.0) -> list[str]` (GET `{base_url}/models` con
  `urllib.request`, restituisce gli `id`; solleva `OSError` se il server non risponde);
  `verifica_modello(base_url: str, modello: str, elenca: Callable[[str], list[str]] = elenca_modelli) -> str | None`.
- Produce in `grafo.py`: `PROMPT_SISTEMA: str`; `crea_grafo(modello: Runnable, strumenti: Sequence[BaseTool] = (), max_passaggi: int = 6) -> CompiledStateGraph`
  (in questo task solo `START → llm → END`; il nodo `llm` invoca `modello` con
  `[SystemMessage(PROMPT_SISTEMA), *stato["messages"]]` e registra a INFO inizio, fine e durata).
- Produce in `conversazione.py`: `class ErroreModello(Exception)`;
  `@dataclass class ChiamataStrumento(nome: str, argomenti: dict, risultato: str)`;
  `@dataclass class EsitoTurno(risposta: str | None, chiamate: list[ChiamataStrumento], limite_raggiunto: bool)`;
  `class Conversazione(grafo, base_url: str)` con attributo `cronologia: list[BaseMessage]` e
  metodo `invia(testo: str) -> EsitoTurno`.

- [ ] **Passo 1: test della configurazione che falliscono** in `tests/test_configurazione.py`:
  - `test_valori_minimi_e_default`: con solo `LMSTUDIO_BASE_URL="http://localhost:1234/v1"` e
    `LMSTUDIO_MODEL="google/gemma-4-e2b"` → `fuso_predefinito == "Europe/Rome"`, `max_passaggi == 6`,
    `livello_log == "WARNING"`.
  - `test_variabile_obbligatoria_mancante` (parametrizzato sulle due obbligatorie, anche valore
    `"  "`): `pytest.raises(ErroreConfigurazione, match=<nome variabile>)`.
  - `test_max_passaggi_non_valido` per `"0"`, `"-1"`, `"sei"` → errore che nomina `MAX_PASSAGGI`.
  - `test_livello_log_non_valido` (`"verbose"`) → errore che nomina `LIVELLO_LOG`; `"info"` è accettato e normalizzato a `"INFO"`.
  - `test_fuso_predefinito_non_valido` (`"Roma"`) → errore che nomina `FUSO_ORARIO_PREDEFINITO`
    (validazione con `zoneinfo.ZoneInfo`; il Task 4 la sposterà su `valida_fuso`).
- [ ] **Passo 2:** `python -m pytest tests/test_configurazione.py -v` → FAIL; implementa
  `configurazione.py`; → PASS.
- [ ] **Passo 3: test di modello e grafo che falliscono.**
  - `tests/test_modello.py`: `test_verifica_modello_presente` (elenca finto con il modello → `None`);
    `test_verifica_modello_assente` (→ `ErroreConfigurazione` il cui messaggio contiene il modello
    richiesto e gli id disponibili); `test_verifica_server_irraggiungibile` (elenca che solleva
    `OSError` → stringa di avviso che contiene il `base_url`, nessuna eccezione).
  - `tests/test_grafo.py` (sostituisce i test del Task 1): con
    `GenericFakeChatModel(messages=iter([AIMessage("Ciao!")]))`,
    `test_grafo_passa_dal_nodo_llm` (aggiornamenti in streaming == `[["llm"]]`, ultimo messaggio
    `"Ciao!"`) e `test_log_della_chiamata_al_modello` (`caplog` a INFO contiene inizio e fine
    della chiamata).
- [ ] **Passo 4:** test FAIL; implementa `modello.py` e `crea_grafo` (rimuovendo
  `crea_grafo_fisso` e `RISPOSTA_FISSA`); → PASS. `PROMPT_SISTEMA`: assistente del laboratorio,
  risponde in italiano, per data e ora usa sempre lo strumento `ora_corrente` e non le inventa.
- [ ] **Passo 5: test della conversazione che falliscono** in `tests/test_conversazione.py`:
  - `test_due_turni_conservano_la_cronologia`: due risposte finte → `cronologia` ha 4 messaggi
    nell'ordine Human/AI/Human/AI con i testi attesi; nessun duplicato.
  - `test_errore_di_connessione_ripristina_la_cronologia`: dopo un turno riuscito, un modello che
    solleva `class ConnessioneRifiutata(openai.APIConnectionError)` (con `__init__` che chiama solo
    `Exception.__init__(self, "Connection refused")`) → `pytest.raises(ErroreModello)` con
    `base_url` e il suggerimento nel messaggio; `cronologia` identica a prima; un turno successivo
    riuscito porta la cronologia a 4 messaggi.
  - `test_errore_http_ripristina_la_cronologia`: stessa cosa con una sottoclasse analoga di
    `openai.APIStatusError` (Focus 3).
  Il modello finto per errori e risposte alternate è un `RunnableLambda` definito nel test.
- [ ] **Passo 6:** test FAIL; implementa `Conversazione.invia`: invoca il grafo con
  `{"messages": [*cronologia, HumanMessage(testo)]}` (il Task 5 aggiungerà `"passaggi": 0` e
  `"limite_raggiunto": False` all'ingresso); intercetta `openai.APIError`
  e rilancia `ErroreModello("Impossibile contattare il modello su {base_url}: {dettaglio}. Controlla che LM Studio sia avviato, che il server sia attivo e che LMSTUDIO_BASE_URL sia corretto.")`;
  in caso di successo sostituisce `cronologia` con i messaggi restituiti; `risposta` = testo
  dell'ultimo `AIMessage`. → PASS.
- [ ] **Passo 7:** `.env.example` con le cinque variabili, `LMSTUDIO_BASE_URL=http://localhost:1234/v1`,
  `LMSTUDIO_MODEL=google/gemma-4-e2b` e il commento «identificativo da GET /v1/models».
- [ ] **Passo 8:** `python -m pytest -v` → tutti passati; commit
  `feat(modello): collega LM Studio e conserva la cronologia della sessione`.

### Task 3: Interfaccia da terminale e avvio (RF-01, RF-11, RF-12, RF-13)

**File:**
- Crea: `assistente/terminale.py`, `assistente/__main__.py`
- Crea: `tests/reali/__init__.py`, `tests/reali/test_lmstudio.py`
- Test: `tests/test_terminale.py`, `tests/test_avvio.py`
- Modifica: `README.md`

**Interfacce:**
- Consuma: `Conversazione`, `EsitoTurno`, `ChiamataStrumento`, `ErroreModello`,
  `carica_configurazione`, `verifica_modello`, `crea_modello`, `crea_grafo`.
- Produce in `terminale.py`: `formatta_chiamata(c: ChiamataStrumento) -> str`;
  `esegui_chat(conversazione, leggi: Callable[[str], str] = input, scrivi: Callable[[str], None] = print) -> None`.
- Produce in `__main__.py`: `main(ambiente: Mapping[str, str] | None = None) -> int`
  (`load_dotenv()`, configurazione, `logging.basicConfig(stream=sys.stderr, level=...)`,
  `verifica_modello`, intestazione `Assistente del laboratorio — modello {modello} su {base_url}` e
  `Scrivi «esci» per terminare.`, poi `esegui_chat`; restituisce 1 con messaggio su stderr in caso di
  `ErroreConfigurazione`, 0 altrimenti); `if __name__ == "__main__": sys.exit(main())`.

- [ ] **Passo 1: test che falliscono** in `tests/test_terminale.py`, con `leggi` che restituisce
  input prestabiliti e `scrivi` che accumula le righe, e una `Conversazione` finta:
  - `test_turno_normale_ed_esci`: input `["ciao", "esci"]` → righe contengono `Assistente> Ciao!`; un solo `invia`.
  - `test_righe_vuote_ignorate`: `["", "   ", "esci"]` → nessun `invia`.
  - `test_fine_input_e_ctrl_c` (parametrizzato): `leggi` solleva `EOFError` o `KeyboardInterrupt` → ritorno senza eccezioni.
  - `test_ctrl_c_durante_la_risposta`: `invia` solleva `KeyboardInterrupt` → ritorno pulito (Focus 5).
  - `test_errore_modello_mostrato_e_sessione_aperta`: primo `invia` solleva `ErroreModello("x")`,
    secondo riesce → righe contengono `Errore: x` e poi la risposta.
  - `test_risposta_vuota`: `risposta=""` → `Assistente> (il modello non ha restituito testo)` (Focus 4).
  - `test_limite_raggiunto`: `EsitoTurno(None, [], True)` → riga con
    `Limite di passaggi raggiunto: nessuna risposta finale. Riformula la domanda.`
  - `test_formatta_chiamata`: `ChiamataStrumento("ora_corrente", {"fuso_orario": "Asia/Tokyo"}, "R")`
    → `[strumento] ora_corrente(fuso_orario="Asia/Tokyo") → R`; con `{}` → `[strumento] ora_corrente() → R`.
    `esegui_chat` stampa una riga per ogni chiamata prima della risposta.
- [ ] **Passo 2:** FAIL → implementa `terminale.py` → PASS.
- [ ] **Passo 3: test che falliscono** in `tests/test_avvio.py`: `main({})` restituisce 1 e
  stderr (`capsys`) nomina `LMSTUDIO_BASE_URL`, senza traceback. Implementa `main` → PASS.
- [ ] **Passo 4: prova reale marcata** `tests/reali/test_lmstudio.py` (`pytestmark = pytest.mark.lmstudio`,
  configurazione da `.env` con `load_dotenv`): `test_due_turni_con_il_modello_reale` — «Mi chiamo Ada.»
  poi «Come mi chiamo?» → la seconda risposta contiene `Ada`.
  Verifica che `python -m pytest` lo escluda (deselected).
- [ ] **Passo 5: prova reale (richiede LM Studio attivo)** — copia `.env.example` in `.env`,
  `python -m pytest -m lmstudio -v` → PASS; poi `python -m assistente`: due turni, `esci`;
  con `$env:LIVELLO_LOG="INFO"` i log mostrano inizio e fine della chiamata. Con LM Studio
  fermo: messaggio di errore e sessione aperta. Annota gli esiti per il resoconto.
- [ ] **Passo 6: README** — configurazione (`Copy-Item .env.example .env`, come leggere
  `GET /v1/models` con `Invoke-RestMethod http://localhost:1234/v1/models`), avvio locale,
  `LIVELLO_LOG`, prove reali con `-m lmstudio`. Solo comandi eseguiti nel Passo 5.
- [ ] **Passo 7:** commit `feat(terminale): aggiungi la chat da terminale e l'avvio` (senza `.env`).

---

## Incremento 3 — Strumento orologio con instradamento

### Task 4: Strumento `ora_corrente` (RF-06, RF-07, RE-03)

**File:**
- Crea: `assistente/strumenti.py`
- Modifica: `assistente/configurazione.py` (usa `valida_fuso`)
- Test: `tests/test_strumenti.py`

**Interfacce:**
- Produce: `valida_fuso(nome: str) -> ZoneInfo` (rimuove gli spazi esterni; solleva `ValueError`
  con messaggio per vuoto, nome sconosciuto o non valido — intercetta sia
  `ZoneInfoNotFoundError` sia `ValueError` di `zoneinfo`);
  `ora_corrente_testo(fuso_orario: str | None, fuso_predefinito: str, adesso_utc: datetime) -> str`;
  `crea_strumento_orologio(fuso_predefinito: str, orologio: Callable[[], datetime] = <datetime.now(timezone.utc)>) -> BaseTool`
  (`StructuredTool.from_function`, nome `ora_corrente`, unico parametro `fuso_orario: str | None = None`).

- [ ] **Passo 1: test che falliscono** con `ISTANTE_INVERNO = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)`
  e `ISTANTE_ESTATE = datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc)`:
  - Roma inverno → `"2026-01-15T13:00:00+01:00 (Europe/Rome)"`; Roma estate → `"2026-07-15T14:00:00+02:00 (Europe/Rome)"`.
  - Tokyo inverno → `"2026-01-15T21:00:00+09:00 (Asia/Tokyo)"`; `UTC` → `"2026-01-15T12:00:00+00:00 (UTC)"`.
  - `None` con default `"Europe/Rome"` → risultato di Roma.
  - `" Asia/Tokyo "` → come Tokyo (Focus 1).
  - Parametrizzato su `"Tokyo"`, `"UTC+2"`, `""`, `"../etc/passwd"`: il risultato inizia con
    `Errore:`, contiene il valore ricevuto e `Asia/Tokyo` come esempio; nessuna eccezione (Focus 1).
  - `test_strumento_langchain`: `crea_strumento_orologio("Europe/Rome", orologio=lambda: ISTANTE_INVERNO)`
    ha `name == "ora_corrente"`, la descrizione contiene `Europe/Rome`, `Asia/Tokyo`,
    `America/New_York`, `UTC`; `.invoke({"fuso_orario": "Asia/Tokyo"})` e `.invoke({})` danno i valori attesi.
- [ ] **Passo 2:** FAIL → implementa (`adesso_utc.astimezone(zona).isoformat(timespec="seconds")`) → PASS.
  La descrizione: restituisce data e ora attuali; usarla ogni volta che servono data o ora
  correnti, senza inventarle; `fuso_orario` è un nome IANA (esempi sopra); se omesso usa il
  fuso predefinito.
- [ ] **Passo 3:** `configurazione.py` usa `valida_fuso`; `python -m pytest -v` → tutti passati.
- [ ] **Passo 4:** commit `feat(strumenti): aggiungi lo strumento orologio con fuso orario esplicito`.

### Task 5: Instradamento, nodo strumenti e limite di passaggi (RF-02, RF-08, RF-09, RF-10, RF-11)

**File:**
- Modifica: `assistente/grafo.py`, `assistente/conversazione.py`, `assistente/__main__.py`
- Modifica: `tests/reali/test_lmstudio.py`, `README.md`
- Test: `tests/test_grafo.py`, `tests/test_conversazione.py`

**Interfacce:**
- Consuma: `crea_strumento_orologio` (Task 4).
- Produce in `grafo.py`: `StatoConversazione` con in più `passaggi: int` e `limite_raggiunto: bool`;
  `instrada(stato: StatoConversazione, max_passaggi: int) -> Literal["strumenti", "fine"]`
  (`"strumenti"` se l'ultimo `AIMessage` ha `tool_calls` e `passaggi < max_passaggi`);
  nodi `"llm"` (incrementa `passaggi`; se ci sono `tool_calls` e `passaggi == max_passaggi`
  imposta `limite_raggiunto=True`) e `"strumenti"`; arco condizionale
  `llm → {"strumenti": "strumenti", "fine": END}`, arco `strumenti → llm`.
- `nodo strumenti`: per ogni `tool_call` dell'ultimo messaggio cerca lo strumento per nome ed
  esegue `invoke(args)`; strumento sconosciuto o eccezione → contenuto `Errore: ...`; aggiunge
  `ToolMessage(content, tool_call_id=..., name=...)`; registra a INFO nome, argomenti e risultato.
  `instrada` registra a INFO la decisione; il limite raggiunto a WARNING.
- `Conversazione.invia`: `chiamate` ricavate dai nuovi messaggi (coppie `tool_calls` ↔ `ToolMessage`
  per `tool_call_id`); l'ingresso del grafo include `"passaggi": 0, "limite_raggiunto": False`;
  se `limite_raggiunto` → `EsitoTurno(None, chiamate, True)` e cronologia invariata.
- `__main__.main` passa `[crea_strumento_orologio(config.fuso_predefinito)]` a `crea_modello` e `crea_grafo`.

- [ ] **Passo 1: test che falliscono** in `tests/test_grafo.py` (modello finto che restituisce prima
  `AIMessage("", tool_calls=[{"name": "ora_corrente", "args": {"fuso_orario": "Asia/Tokyo"}, "id": "call_1"}])`
  poi `AIMessage("A Tokyo sono le 21:00.")`, strumento con istante fisso):
  - `test_percorso_con_strumento`: nodi visitati `["llm", "strumenti", "llm"]`; il `ToolMessage` ha
    `tool_call_id == "call_1"` e contenuto `"2026-01-15T21:00:00+09:00 (Asia/Tokyo)"`.
  - `test_percorso_senza_strumento`: nodi `["llm"]`.
  - `test_limite_di_passaggi`: modello che chiede sempre lo strumento, `max_passaggi=3` →
    `llm` eseguito 3 volte, `strumenti` 2, `limite_raggiunto is True`.
  - `test_strumento_sconosciuto_e_argomenti_errati` (parametrizzato su nome `"meteo"` e args
    `{"timezone": "Asia/Tokyo"}`): `ToolMessage` che inizia con `Errore:`, il grafo torna a `llm` (Focus 2).
  - `test_log_della_chiamata_allo_strumento`: `caplog` a INFO contiene `ora_corrente` e `Asia/Tokyo`.
  - `test_instrada` sui quattro casi (con/senza tool_calls × sotto/al limite).
- [ ] **Passo 2:** FAIL → implementa → PASS.
- [ ] **Passo 3: test che falliscono** in `tests/test_conversazione.py`:
  `test_esito_con_chiamate` (`EsitoTurno.chiamate == [ChiamataStrumento("ora_corrente", {"fuso_orario": "Asia/Tokyo"}, "2026-01-15T21:00:00+09:00 (Asia/Tokyo)")]`);
  `test_limite_ripristina_la_cronologia` (cronologia invariata, poi un turno normale porta a 2 messaggi). FAIL → implementa → PASS.
- [ ] **Passo 4: prova reale marcata** in `tests/reali/test_lmstudio.py`:
  `test_domanda_sull_ora_usa_lo_strumento` — «Che ore sono adesso a Tokyo?» → almeno una chiamata
  `ora_corrente` con `fuso_orario` che normalizzato è `Asia/Tokyo`, risultato senza `Errore:`, e la
  risposta contiene l'ora `HH:MM` del risultato; `test_domanda_ordinaria_senza_strumento` —
  «Qual è la capitale della Francia?» → nessuna chiamata.
- [ ] **Passo 5: prova reale (richiede LM Studio)** — `python -m pytest -m lmstudio -v`, poi
  `python -m assistente` con `$env:LIVELLO_LOG="INFO"` e domande su Tokyo e su Roma: riga
  `[strumento]` in chat e log di richiesta, esecuzione e risultato. **Se `google/gemma-4-e2b` non
  chiede lo strumento in modo affidabile, non modificare i test per farli passare: annota il
  problema e fermati per discuterne con l'utente.**
- [ ] **Passo 6: README** — sezione «Strumento orologio»: contratto, esempio di riga
  `[strumento]`, come vedere i log, che cosa dimostra la prova reale.
- [ ] **Passo 7:** commit `feat(grafo): instrada le richieste di tool verso lo strumento orologio con limite di passaggi`.

---

## Incremento 4 — Docker Compose

### Task 6: Container con LM Studio sull'host (RE-01, RE-02, RE-03)

**File:**
- Crea: `Dockerfile`, `compose.yaml`, `.dockerignore`, `tests/reali/test_docker.py`
- Modifica: `README.md`

- [ ] **Passo 1: `Dockerfile`** — `FROM python:3.13-slim`; `ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1`;
  `WORKDIR /app`; copia e installa `requirements.txt` con `pip install --no-cache-dir`; copia
  `assistente/`; `CMD ["python", "-m", "assistente"]`.
- [ ] **Passo 2: `compose.yaml`** — servizio `assistente` con `build: .`, `env_file: .env`,
  `environment: LMSTUDIO_BASE_URL: http://host.docker.internal:1234/v1` (prevale su `.env`),
  `extra_hosts: ["host.docker.internal:host-gateway"]`, `stdin_open: true`, `tty: true`; nessuna porta.
- [ ] **Passo 3: `.dockerignore`** — `.env`, `.venv`, `__pycache__`, `.pytest_cache`, `.git`, `tests`, `docs`.
- [ ] **Passo 4: prova reale marcata** `tests/reali/test_docker.py` (`pytest.mark.docker`):
  `subprocess.run(["docker", "compose", "run", "--rm", "-T", "assistente"], input="Che ore sono adesso a Tokyo?\nesci\n", text=True, encoding="utf-8", capture_output=True, timeout=300, cwd=<radice del progetto>)`
  → `returncode == 0` e stdout contiene `[strumento] ora_corrente(` e `Asia/Tokyo`.
- [ ] **Passo 5: prova reale (richiede Docker e LM Studio)** — `docker compose build`;
  `python -m pytest -m docker -v`; poi interattivo come nella slide 17:
  `docker compose run --rm --name assistente-demo assistente` e, da un secondo terminale,
  `docker ps` e `docker logs -f assistente-demo` (con `LIVELLO_LOG=INFO` in `.env`). Se il
  container non raggiunge LM Studio: attivare in LM Studio il servizio sulla rete locale e
  controllare il firewall; annotare cosa è servito.
- [ ] **Passo 6: README** — sezione Docker con i comandi del Passo 5 e una tabella di diagnosi
  (container che termina subito, nessuna connessione al modello, risposta senza orologio),
  più la nota che a `INFO` i log compaiono anche nel terminale della chat.
- [ ] **Passo 7:** commit `feat(docker): avvia l'assistente con Docker Compose e LM Studio sull'host`.

---

## Incremento 5 — Verifica completa

### Task 7: Review e verifica finale (RV-01…RV-06)

**File:**
- Modifica: `README.md`, `CLAUDE.md` (solo convenzioni stabili: struttura, comandi di test)

- [ ] **Passo 1:** `python -m pytest -v` → tutti passati, prove reali deselezionate.
- [ ] **Passo 2:** `python -m pytest -m lmstudio -v` e `python -m pytest -m docker -v` → esiti annotati.
- [ ] **Passo 3:** review dell'intero lavoro rispetto alla specifica con `superpowers:requesting-code-review`;
  correggi i problemi confermati con un ciclo test → correzione.
- [ ] **Passo 4:** ripercorri ogni riga della tabella della sezione 8 della specifica e ogni
  comando del README eseguendolo davvero; togli dal README ciò che non è stato verificato.
- [ ] **Passo 5:** aggiorna `CLAUDE.md` con la struttura del progetto e i comandi di test
  (`python -m pytest`, `-m lmstudio`, `-m docker`).
- [ ] **Passo 6:** commit `docs: completa README e CLAUDE.md dopo la verifica finale`.
- [ ] **Passo 7: resoconto** all'utente: prove eseguite con esito, problemi aperti, `git status`,
  `git log --oneline`; chiedere prima di qualsiasi push.
