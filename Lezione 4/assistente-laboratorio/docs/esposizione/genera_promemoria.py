"""Genera il promemoria di 5 pagine per l'esposizione dell'assistente del laboratorio.

È la versione breve di genera_pdf.py (la guida completa): una pagina per argomento, da ripassare
prima di parlare. Non fa parte dell'applicazione: reportlab non è tra le sue dipendenze. Usa i font
di Windows (Segoe UI e Consolas). Da PowerShell, dalla cartella assistente-laboratorio:

    python -m venv $env:TEMP\\pdfenv
    & $env:TEMP\\pdfenv\\Scripts\\python.exe -m pip install reportlab==5.1.0
    & $env:TEMP\\pdfenv\\Scripts\\python.exe docs\\esposizione\\genera_promemoria.py docs\\esposizione\\assistente-laboratorio-promemoria.pdf
"""

import math
import sys

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

USCITA = sys.argv[1]
PAGINE_ATTESE = 5
FONT = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Testo", FONT + "segoeui.ttf"))
pdfmetrics.registerFont(TTFont("Testo-B", FONT + "segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Testo-I", FONT + "segoeuii.ttf"))
pdfmetrics.registerFont(TTFont("Codice", FONT + "consola.ttf"))
pdfmetrics.registerFontFamily("Testo", normal="Testo", bold="Testo-B", italic="Testo-I", boldItalic="Testo-B")

BLU = colors.HexColor("#1F3A5F")
BLU_CHIARO = colors.HexColor("#E8EEF6")
ACCENTO = colors.HexColor("#C2622D")
GRIGIO = colors.HexColor("#5A6270")
GRIGIO_CHIARO = colors.HexColor("#F3F4F6")
BORDO = colors.HexColor("#CBD2DC")
VERDE = colors.HexColor("#2E7D4F")
VERDE_CHIARO = colors.HexColor("#E7F4EC")
GIALLO_CHIARO = colors.HexColor("#FFF6E0")

MARGINE = 1.8 * cm
LARGHEZZA = A4[0] - 2 * MARGINE  # 17,4 cm

S = {
    "h1": ParagraphStyle("h1", fontName="Testo-B", fontSize=15, leading=19, textColor=BLU, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="Testo-B", fontSize=10.8, leading=14, textColor=ACCENTO, spaceBefore=6, spaceAfter=3),
    "corpo": ParagraphStyle("corpo", fontName="Testo", fontSize=9, leading=12.4, spaceAfter=3),
    "punto": ParagraphStyle("punto", fontName="Testo", fontSize=9, leading=12.2, leftIndent=12, bulletIndent=2, spaceAfter=1.5),
    "cella": ParagraphStyle("cella", fontName="Testo", fontSize=8.3, leading=10.6),
    "cella_b": ParagraphStyle("cella_b", fontName="Testo-B", fontSize=8.3, leading=10.6, textColor=colors.white),
    "codice": ParagraphStyle("codice", fontName="Codice", fontSize=7.8, leading=9.8, textColor=colors.HexColor("#1D2430")),
    "riquadro": ParagraphStyle("riquadro", fontName="Testo", fontSize=9, leading=12.4),
    "nota": ParagraphStyle("nota", fontName="Testo-I", fontSize=8, leading=10.5, textColor=GRIGIO, spaceAfter=3),
    "domanda": ParagraphStyle("domanda", fontName="Testo-B", fontSize=8.3, leading=10.6, textColor=BLU),
}

storia = []


def nuova_pagina():
    """Salto pagina senza lo spazio finale, che altrimenti potrebbe scivolare su una pagina vuota."""
    while storia and isinstance(storia[-1], Spacer):
        storia.pop()
    storia.append(PageBreak())


def c(testo):
    """Testo in carattere a larghezza fissa dentro un paragrafo."""
    return f"<font name='Codice'>{testo}</font>"


def h1(testo):
    storia.append(Paragraph(testo, S["h1"]))


def h2(testo):
    storia.append(Paragraph(testo, S["h2"]))


def p(testo):
    storia.append(Paragraph(testo, S["corpo"]))


def punti(*voci):
    for voce in voci:
        storia.append(Paragraph(voce, S["punto"], bulletText="•"))
    storia.append(Spacer(1, 2))


def codice(testo):
    righe_lunghe = [r for r in testo.strip("\n").splitlines() if len(r) > 111]
    if righe_lunghe:
        raise SystemExit(f"Righe di codice troppo lunghe: {righe_lunghe}")
    t = Table([[Preformatted(testo.strip("\n"), S["codice"])]], colWidths=[LARGHEZZA])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIGIO_CHIARO),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D9E0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    storia.append(t)
    storia.append(Spacer(1, 5))


def riquadro(titolo, testo, sfondo=BLU_CHIARO, bordo=BLU):
    contenuto = [Paragraph(f"<b>{titolo}</b>", S["riquadro"]), Paragraph(testo, S["riquadro"])]
    t = Table([[contenuto]], colWidths=[LARGHEZZA])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), sfondo),
        ("LINEBEFORE", (0, 0), (0, -1), 3, bordo),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    storia.append(KeepTogether([t, Spacer(1, 6)]))


def tabella(intestazione, righe, larghezze, stile_prima_colonna="cella"):
    """Tabella con intestazione blu; le larghezze in cm devono sommare a 17,4."""
    assert abs(sum(larghezze) - LARGHEZZA / cm) < 0.01, (intestazione, sum(larghezze))
    dati = [[Paragraph(x, S["cella_b"]) for x in intestazione]]
    for riga in righe:
        dati.append([Paragraph(x, S[stile_prima_colonna] if i == 0 else S["cella"]) for i, x in enumerate(riga)])
    t = Table(dati, colWidths=[l * cm for l in larghezze], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLU),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIGIO_CHIARO]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5), ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.8),
    ]))
    storia.append(t)
    storia.append(Spacer(1, 6))


def affiancati(sinistra, destra, quota_sinistra=0.5, spazio=0.4 * cm):
    """Due colonne di flowable una accanto all'altra."""
    l1 = (LARGHEZZA - spazio) * quota_sinistra
    l2 = LARGHEZZA - spazio - l1
    t = Table([[sinistra, "", destra]], colWidths=[l1, spazio, l2])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    storia.append(t)


def scheda(titolo, voci, sfondo=BLU_CHIARO, bordo=BLU):
    """Riquadro con titolo e punti, da usare dentro affiancati()."""
    contenuto = [Paragraph(f"<b>{titolo}</b>", S["riquadro"])]
    contenuto += [Paragraph(v, S["punto"], bulletText="•") for v in voci]
    t = Table([[contenuto]])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), sfondo),
        ("LINEBEFORE", (0, 0), (0, -1), 3, bordo),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


# ---------- diagrammi (gli stessi della guida completa) ----------

def scatola(d, x, y, w, h, testo, sotto="", sfondo=BLU_CHIARO, bordo=BLU, dim=10):
    d.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=sfondo, strokeColor=bordo, strokeWidth=1.2))
    if sotto:
        d.add(String(x + w / 2, y + h / 2 + 2, testo, fontName="Testo-B", fontSize=dim, fillColor=bordo, textAnchor="middle"))
        d.add(String(x + w / 2, y + h / 2 - 10, sotto, fontName="Testo", fontSize=7.5, fillColor=GRIGIO, textAnchor="middle"))
    else:
        d.add(String(x + w / 2, y + h / 2 - 3.5, testo, fontName="Testo-B", fontSize=dim, fillColor=bordo, textAnchor="middle"))


def freccia(d, x1, y1, x2, y2, colore=GRIGIO, etichetta="", ex=0, ey=0):
    d.add(Line(x1, y1, x2, y2, strokeColor=colore, strokeWidth=1.3))
    a = math.atan2(y2 - y1, x2 - x1)
    d.add(Polygon([x2, y2, x2 - 7 * math.cos(a - 0.4), y2 - 7 * math.sin(a - 0.4),
                   x2 - 7 * math.cos(a + 0.4), y2 - 7 * math.sin(a + 0.4)], fillColor=colore, strokeColor=colore))
    if etichetta:
        d.add(String((x1 + x2) / 2 + ex, (y1 + y2) / 2 + ey, etichetta, fontName="Testo-I", fontSize=8,
                     fillColor=colore, textAnchor="middle"))


def ridimensiona(d, fattore):
    d.scale(fattore, fattore)
    d.width *= fattore
    d.height *= fattore
    return d


def diagramma_grafo():
    d = Drawing(465, 200)
    scatola(d, 10, 135, 70, 34, "START", sfondo=colors.white)
    scatola(d, 125, 125, 120, 54, "llm", "messaggi + descrizione strumento")
    rx, ry = 330, 152
    d.add(Polygon([rx, ry + 32, rx + 55, ry, rx, ry - 32, rx - 55, ry], fillColor=GIALLO_CHIARO, strokeColor=ACCENTO, strokeWidth=1.2))
    d.add(String(rx, ry + 3, "instrada()", fontName="Testo-B", fontSize=9, fillColor=ACCENTO, textAnchor="middle"))
    d.add(String(rx, ry - 9, "tool_calls?", fontName="Testo", fontSize=7.5, fillColor=GRIGIO, textAnchor="middle"))
    scatola(d, 405, 135, 55, 34, "END", sfondo=colors.white)
    scatola(d, 270, 5, 120, 54, "strumenti", "esegue ora_corrente", sfondo=VERDE_CHIARO, bordo=VERDE)
    freccia(d, 80, 152, 125, 152)
    freccia(d, 245, 152, 275, 152)
    freccia(d, 385, 152, 405, 152, etichetta="no / limite", ex=-6, ey=16)
    freccia(d, rx, ry - 32, rx, 59, colore=VERDE, etichetta="sì e passaggi < max", ex=48)
    d.add(Line(270, 32, 185, 32, strokeColor=VERDE, strokeWidth=1.3))
    freccia(d, 185, 32, 185, 125, colore=VERDE, etichetta="ToolMessage", ex=-34)
    return d


def diagramma_architettura():
    d = Drawing(465, 262)
    d.add(Rect(5, 32, 330, 225, rx=8, ry=8, fillColor=None, strokeColor=GRIGIO, strokeWidth=1, strokeDashArray=[4, 3]))
    d.add(String(12, 244, "Processo Python (in locale o nel container Docker)", fontName="Testo-I", fontSize=8, fillColor=GRIGIO))
    scatola(d, 20, 167, 130, 44, "terminale", "input / output della chat")
    scatola(d, 185, 167, 135, 44, "conversazione", "cronologia + rollback")
    scatola(d, 185, 102, 135, 44, "grafo", "stato, llm, strumenti")
    scatola(d, 20, 102, 130, 44, "strumenti", "ora_corrente", sfondo=VERDE_CHIARO, bordo=VERDE)
    scatola(d, 185, 42, 135, 44, "modello", "ChatOpenAI + bind_tools")
    scatola(d, 20, 42, 130, 44, "configurazione", "variabili d'ambiente")
    scatola(d, 365, 42, 95, 44, "LM Studio", "sull'host :1234", sfondo=GIALLO_CHIARO, bordo=ACCENTO)
    scatola(d, 365, 167, 95, 44, "utente", "Tu> / Assistente>", sfondo=colors.white)
    d.add(Line(412, 211, 412, 228, strokeColor=GRIGIO, strokeWidth=1.3))
    d.add(Line(412, 228, 85, 228, strokeColor=GRIGIO, strokeWidth=1.3))
    freccia(d, 85, 228, 85, 211)
    d.add(String(250, 232, "domande e risposte", fontName="Testo-I", fontSize=8, fillColor=GRIGIO, textAnchor="middle"))
    freccia(d, 150, 189, 185, 189)
    freccia(d, 252, 167, 252, 146)
    freccia(d, 185, 124, 150, 124, etichetta="invoke", ey=4)
    freccia(d, 252, 102, 252, 86)
    freccia(d, 320, 64, 365, 64, colore=ACCENTO, etichetta="HTTP /v1", ey=5)
    freccia(d, 150, 64, 185, 64)
    d.add(String(232, 14, "__main__ legge la configurazione, crea strumento, modello, grafo e conversazione, poi avvia la chat",
                 fontName="Testo-I", fontSize=8, fillColor=GRIGIO, textAnchor="middle"))
    return d


# ---------- pagine ----------

TITOLI = {
    1: "Il progetto in un minuto",
    2: "La teoria essenziale",
    3: "Come è fatto",
    4: "Test, metodo e risultati",
    5: "L'esposizione: scaletta, demo, domande",
}


def intestazione_e_piede(canvas, doc):
    canvas.saveState()
    alto = A4[1]
    canvas.setFillColor(BLU)
    canvas.rect(0, alto - 1.25 * cm, A4[0], 1.25 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Testo-B", 10)
    canvas.drawString(MARGINE, alto - 0.8 * cm, "Assistente del laboratorio · promemoria per l'esposizione")
    canvas.setFont("Testo", 9)
    canvas.drawRightString(A4[0] - MARGINE, alto - 0.8 * cm, f"{doc.page}/{PAGINE_ATTESE} · {TITOLI.get(doc.page, '')}")
    canvas.setFillColor(GRIGIO)
    canvas.setFont("Testo", 7.5)
    canvas.drawString(MARGINE, 1.0 * cm, "Deep Learning e LLM · Lezione 4 · Dal client a un agente LangGraph · "
                                         "guida completa: assistente-laboratorio-esposizione.pdf")
    canvas.drawRightString(A4[0] - MARGINE, 1.0 * cm, f"pagina {doc.page} di {PAGINE_ATTESE}")
    canvas.restoreState()


# ===== Pagina 1 =====
h1("1 · Il progetto in un minuto")
riquadro("Se devi dirlo in 30 secondi",
         "È un <b>chatbot da terminale</b> in Python che parla con un <b>modello locale</b> (Gemma 4 in LM Studio). "
         "Il flusso è un <b>grafo LangGraph</b> esplicito: un nodo chiama il modello, un nodo esegue gli strumenti, una "
         "funzione decide dove andare. Quando chiedi l'ora il modello <b>non la inventa</b>: chiede lo strumento "
         "<b>orologio</b>, il programma lo esegue davvero e il risultato torna al modello. La cronologia dura per la "
         "sessione, si avvia anche con <b>Docker Compose</b> e ci sono <b>70 test</b> che non richiedono il modello.")
affiancati(
    scheda("Le cinque idee da far passare", [
        "<b>Il modello è senza stato</b>: la memoria è dell'applicazione, che reinvia la cronologia a ogni turno.",
        "<b>Il modello chiede, il programma esegue</b>: il tool calling è una richiesta strutturata, non un'esecuzione.",
        "<b>Grafo esplicito</b>: stato, nodi e instradamento si vedono, si testano e si estendono.",
        "<b>Nessuna risposta inventata</b>: errori chiari, limite di passaggi, rollback del turno.",
        "<b>Verificato davvero</b>: test senza modello + prove reali con LM Studio e Docker.",
    ]),
    scheda("Numeri da ricordare", [
        f"Modello {c('google/gemma-4-e2b')}, GGUF Q4_K_M, contesto 8192 token.",
        "Python 3.13 · LangGraph 1.2.18 · langchain-openai 1.7.3.",
        "7 moduli, 467 righe di codice.",
        "<b>70</b> test automatici + <b>3</b> prove reali LM Studio + <b>1</b> prova Docker.",
        "Tool calling corretto: da <b>12/17</b> a <b>12/12</b> dopo aver migliorato la descrizione.",
        f"{c('MAX_PASSAGGI')} predefinito: 6 chiamate al modello per turno.",
    ], sfondo=GIALLO_CHIARO, bordo=ACCENTO),
    quota_sinistra=0.52,
)
storia.append(Spacer(1, 6))
h2("Il grafo: lo schema da disegnare alla lavagna")
grafo = ridimensiona(diagramma_grafo(), 0.8)
grafo.hAlign = "CENTER"
storia.append(grafo)
storia.append(Paragraph("START → llm → (strumenti → llm)* → END. Si esce quando il modello non chiede più strumenti "
                        f"oppure al limite di passaggi. {c('instrada()')} è scritta nel progetto, così la decisione è "
                        "leggibile e finisce nei log.", S["nota"]))
h2("Come appare una sessione (prova reale del 28 ottobre)")
codice("""
Tu> Che ore sono adesso a Tokyo?
[strumento] ora_corrente(fuso_orario="Asia/Tokyo") → 2026-10-28T20:08:51+09:00 (Asia/Tokyo), mercoledì
Assistente> Adesso sono le 20:08:51 di mercoledì 28 ottobre 2026 a Tokyo.
Tu> Che giorno della settimana è oggi a New York?
[strumento] ora_corrente(fuso_orario="America/New_York")
            → 2026-10-28T07:09:08-04:00 (America/New_York), mercoledì
Assistente> Oggi a New York è mercoledì.
""")
h2("Requisiti della consegna (slide 26)")
tabella(["Requisito", "Evidenza", "Stato"], [
    ["Grafo con LLM e cronologia", "Al secondo turno il modello ricorda «Ada» (prova reale)", "Fatto"],
    ["Strumento orologio", "Riga [strumento] in chat e log INFO di richiesta e risultato", "Fatto"],
    ["Docker Compose", "Prova -m docker superata; chat interattiva provata a mano", "Fatto"],
    ["Test e documentazione", "70 automatici + prove reali; README, AVVIO.md e CLAUDE.md", "Fatto"],
    ["Repository condivisa", "Conventional Commits in italiano; push su origin/main", "Fatto"],
], [3.8, 8.0, 5.6])
nuova_pagina()

# ===== Pagina 2 =====
h1("2 · La teoria essenziale")
h2("LLM locale e LM Studio")
punti(
    "Un LLM prevede il <b>token successivo</b>. Ne derivano tre proprietà: è <b>senza stato</b> (ogni chiamata è "
    "indipendente, la cronologia va reinviata), <b>non ha accesso al mondo</b> (non legge l'orologio: serve uno "
    "strumento), è <b>probabilistico</b> (le prove reali vanno ripetute e contate, es. 12 su 12).",
    f"<b>LM Studio</b> esegue modelli GGUF sul PC e li espone con un'<b>API compatibile con OpenAI</b> su "
    f"{c('http://localhost:1234/v1')}. Il progetto usa {c('GET /v1/models')} all'avvio (il modello configurato esiste?) e "
    f"{c('POST /v1/chat/completions')} a ogni chiamata. Client: <b>ChatOpenAI</b> con un altro {c('base_url')}.",
    "<b>Quantizzazione Q4_K_M</b>: pesi a circa 4 bit invece di 16, così il modello gira su un PC con poca perdita di qualità.",
    f"Ruoli dei messaggi: <b>system</b> (istruzioni), <b>user</b> (domanda), <b>assistant</b> (risposta o {c('tool_calls')}), "
    f"<b>tool</b> (risultato, legato alla richiesta dal {c('tool_call_id')}).",
)
h2("LangGraph: il flusso diventa un grafo")
tabella(["Elemento", "Che cos'è", "Nel progetto"], [
    ["Stato", "Dati condivisi durante l'esecuzione (TypedDict)", f"{c('messages')}, {c('passaggi')}, {c('limite_raggiunto')}"],
    ["Nodo", "Funzione: legge lo stato, restituisce un aggiornamento parziale", f"{c('llm')} e {c('strumenti')}"],
    ["Arco / arco condizionale", "Collegamento fisso / scelto da una funzione sullo stato", f"START → llm, strumenti → llm / {c('instrada()')}"],
    ["Reducer", "Regola che combina l'aggiornamento con lo stato", f"{c('add_messages')}: <b>aggiunge</b> i messaggi, non sostituisce la lista"],
    ["compile / invoke", "Grafo eseguibile / esecuzione che restituisce lo stato finale", f"{c('stream(stream_mode=\"updates\")')} nei test per vedere i nodi"],
    ["Ciclo", "Arco che torna indietro: base degli <b>agenti</b>", "strumenti → llm, con uscita garantita dal limite"],
], [3.6, 6.6, 7.2])
h2("Tool calling: il modello chiede, il programma esegue")
tabella(["Passo", "Chi", "Che cosa succede"], [
    ["1", "Programma", f"Invia i messaggi e, nel campo {c('tools')}, lo strumento descritto in <b>JSON Schema</b> (nome, descrizione, parametri)."],
    ["2", "Modello", f"Se serve risponde con {c('tool_calls')}: nome, argomenti JSON e un id (es. {c('call_1')})."],
    ["3", "Programma", f"Il nodo strumenti esegue la funzione reale e aggiunge un <b>ToolMessage</b> con lo stesso {c('tool_call_id')}."],
    ["4", "Modello", "Legge il risultato e risponde (o chiede un altro strumento)."],
], [1.3, 2.2, 13.9])
riquadro("La descrizione è il contratto",
         "È l'unica cosa che il modello sa dello strumento. Senza la descrizione del parametro il modello ometteva "
         f"{c('fuso_orario')} in 5 casi su 17 (e dava l'ora di Roma); con descrizione del parametro e una frase nel prompt: 12 su 12.")
affiancati(
    scheda("Tempo e fusi orari", [
        "L'istante si legge <b>sempre in UTC</b> e si converte nel fuso richiesto: il fuso del PC o del container non conta.",
        f"<b>Fuso IANA</b> ({c('Europe/Rome')}, {c('Asia/Tokyo')}): conosce l'ora legale; un offset fisso no.",
        f"<b>ISO 8601</b>: {c('2026-10-28T20:08:51+09:00')}.",
        "<b>zoneinfo</b> + <b>tzdata</b> (database dei fusi, assente su Windows e nell'immagine slim).",
        "Giorno della settimana calcolato nel fuso richiesto, con nomi italiani da tabella.",
    ], sfondo=VERDE_CHIARO, bordo=VERDE),
    scheda("Docker e Docker Compose", [
        "<b>Immagine</b> = pacchetto immutabile; <b>container</b> = istanza in esecuzione.",
        f"Dockerfile: {c('python:3.13-slim')}, prima i requirements poi il codice (cache dei layer).",
        f"Il container raggiunge LM Studio su {c('host.docker.internal:1234')}: nel container {c('localhost')} è il container stesso.",
        f"{c('environment')} prevale su {c('env_file')}; {c('stdin_open')} + {c('tty')} per la chat.",
        f"Chat con {c('docker compose run')}, non {c('up')}. LM Studio <b>non</b> va containerizzato.",
    ]),
)
nuova_pagina()

# ===== Pagina 3 =====
h1("3 · Come è fatto")
architettura = ridimensiona(diagramma_architettura(), 0.86)
architettura.hAlign = "CENTER"
storia.append(architettura)
storia.append(Paragraph("Moduli piccoli, una responsabilità ciascuno. Le lezioni successive estenderanno questo codice: "
                        f"un nuovo strumento è un altro BaseTool aggiunto alla lista {c('strumenti')}.", S["nota"]))
tabella(["Modulo", "Responsabilità"], [
    [c("configurazione.py"), "Legge e valida le variabili d'ambiente; l'errore nomina la variabile."],
    [c("strumenti.py"), f"{c('ora_corrente(fuso_orario?)')}: validazione del fuso IANA e formato del risultato."],
    [c("modello.py"), f"ChatOpenAI verso LM Studio con {c('bind_tools')}; controllo di GET /v1/models."],
    [c("grafo.py"), f"Stato, nodi llm e strumenti, {c('instrada')}, limite di passaggi, log."],
    [c("conversazione.py"), "Cronologia di sessione, rollback del turno, errori del modello."],
    [c("terminale.py") + " · " + c("__main__.py"), "Ciclo Tu&gt; / Assistente&gt;, righe [strumento]; avvio e composizione dei pezzi."],
], [5.0, 12.4])
h2("Un turno passo per passo: «Che ore sono adesso a Tokyo?»")
tabella(["#", "Messaggio", "Prodotto da", "Contenuto"], [
    ["1", "HumanMessage", "Conversazione", "Che ore sono adesso a Tokyo?"],
    ["2", "AIMessage", "nodo llm (passaggio 1)", f"testo vuoto + {c('tool_calls')}: ora_corrente({{\"fuso_orario\": \"Asia/Tokyo\"}}), id call_…"],
    ["3", "ToolMessage", "nodo strumenti", "2026-10-28T20:08:51+09:00 (Asia/Tokyo), mercoledì · stesso tool_call_id"],
    ["4", "AIMessage", "nodo llm (passaggio 2)", "Adesso sono le 20:08:51 di mercoledì 28 ottobre 2026 a Tokyo."],
], [0.6, 2.6, 3.6, 10.6])
p(f"Con {c('LIVELLO_LOG=INFO')} i log mostrano: inizio e fine di ogni chiamata al modello con la durata, la decisione di "
  "<b>instradamento</b>, la richiesta di strumento con gli argomenti e il risultato. Alla domanda successiva «E a Roma?» il "
  f"modello passa {c('Europe/Rome')}: ha capito il riferimento grazie alla cronologia.")
affiancati(
    scheda("Cronologia e rollback", [
        f"<b>Conversazione</b> invoca il grafo con {c('[*cronologia, HumanMessage(testo)]')} e {c('passaggi=0')}.",
        "La cronologia viene sostituita <b>solo se il turno riesce</b>.",
        "Se il turno fallisce torna esattamente com'era: niente domanda orfana, niente richieste di tool senza risposta.",
        "<b>Niente checkpointer</b>: la persistenza non è richiesta e il rollback resta semplice.",
    ], sfondo=VERDE_CHIARO, bordo=VERDE),
    scheda("Errori: mai una risposta inventata", [
        "LM Studio spento: avviso all'avvio, errore chiaro in chat, sessione aperta.",
        "Modello inesistente o configurazione errata: uscita con codice 1 e messaggio chiaro, senza traceback.",
        f"Strumento sconosciuto, argomenti errati o non JSON: ToolMessage che inizia con {c('Errore:')}.",
        "Limite di passaggi (3 llm, 2 strumenti con MAX=3): messaggio esplicito + rollback.",
        "Ctrl+C, fine input, «esci»: uscita pulita.",
    ], sfondo=GIALLO_CHIARO, bordo=ACCENTO),
)
nuova_pagina()

# ===== Pagina 4 =====
h1("4 · Test, metodo e risultati")
h2("Due livelli di verifica")
tabella(["Livello", "Che cosa prova", "Comando · esito"], [
    ["Test automatici (70)", "Il <b>programma</b>: percorsi del grafo, ToolMessage, limite, rollback, log, orologio con istante "
     "fisso (Roma inverno/estate, Tokyo, UTC, cambio di giorno), configurazione, terminale, avvio.",
     f"{c('python -m pytest')}<br/>70 passed, 4 deselected"],
    ["Prove reali LM Studio (3)", "Il <b>modello</b>: ricorda «Ada» al secondo turno; chiede davvero l'orologio per Tokyo e usa "
     "l'ora restituita; non usa lo strumento per una domanda ordinaria.", f"{c('python -m pytest -m lmstudio -v')}<br/>3 passed"],
    ["Prova Docker (1)", "Dal container: riga [strumento] con Asia/Tokyo e risposta che usa quell'ora.",
     f"{c('docker compose build')}, poi<br/>{c('python -m pytest -m docker -v')}<br/>1 passed"],
], [3.4, 8.0, 6.0])
punti(
    f"<b>Modelli finti</b> ({c('tests/finti.py')}): GenericFakeChatModel e un RunnableLambda «a copione» restituiscono testo, "
    "richieste di tool o eccezioni: si provano tutti i percorsi senza LM Studio.",
    f"<b>Dipendenze iniettabili</b>: l'orologio ({c('orologio=lambda: ISTANTE_INVERNO')}) e le funzioni leggi/scrivi del terminale.",
    "<b>TDD</b>: ogni funzionalità e ogni correzione è partita da un test visto fallire (RED → GREEN).",
    "Una risposta simulata <b>non</b> dimostra che il modello sappia usare lo strumento: per questo esistono le prove reali.",
)
h2("Metodo di lavoro")
tabella(["Fase (Superpowers)", "Che cosa è stato prodotto"], [
    ["CLAUDE.md", "Istruzioni stabili per Claude Code: obiettivo, confini, scelte tecniche, test, regole Git."],
    ["Brainstorming → specifica", "Decisioni con lo studente; specifica e requisiti con ID (RF, RE, RV) in docs/superpowers."],
    ["Piano → implementazione", "Cinque incrementi con test da scrivere prima; un commit per incremento verificato."],
    ["Revisione indipendente", "Nessun problema critico; 5 problemi importanti corretti partendo da un test che falliva."],
    ["Git", f"Conventional Commits in italiano ({c('feat(grafo): …')}, {c('fix(avvio): …')}), staging selettivo, push su richiesta."],
], [4.4, 13.0])
h2("Risultati e decisioni")
tabella(["Versione dello strumento", "Ora a Tokyo con fuso giusto", "Domanda senza strumento"], [
    ["Senza descrizione del parametro", "12 su 17 (5 volte senza fuso: ora di Roma)", "9 su 9"],
    ["Con descrizione del parametro + frase nel prompt", "<b>12 su 12</b>", "<b>12 su 12</b>"],
], [6.6, 6.6, 4.2])
punti(
    "Il modello non ha mai inventato l'ora: mancava l'argomento. <b>Il test non è stato ammorbidito, è stato migliorato il contratto.</b>",
    "Giorno della settimana: il modello aveva scritto «lunedì» (era mercoledì) → ora il giorno è nel risultato dello strumento.",
    "<b>Lentezza</b>: Gemma 4 genera un <b>ragionamento nascosto</b> di 140–195 token (circa il 90% dei token) a circa 16 "
    f"token/s. Con {c('reasoning_effort=\"none\"')} una risposta scende da 11,9 s a 3,6 s, ma non è stato adottato: "
    "l'affidabilità 12/12 va rimisurata prima.",
)
h2("Limiti e punti aperti (dirli prima che li chiedano)")
punti(
    "LM Studio spento e Ctrl+C dal vivo coperti dai test ma non provati a mano.",
    "La prova Docker non ricostruisce l'immagine: prima va fatto docker compose build.",
)
nuova_pagina()

# ===== Pagina 5 =====
h1("5 · L'esposizione: scaletta, demo, domande")
tabella(["Tempo", "Parte", "Messaggio chiave"], [
    ["1 min", "Obiettivo", "Chatbot locale con grafo esplicito, orologio reale, Docker; requisiti della slide 26."],
    ["2 min", "LangGraph", "Stato, nodi, archi, add_messages; dal grafo fisso al ciclo con strumenti (schema di pagina 1)."],
    ["2 min", "Tool calling", "Il modello chiede, il programma esegue; la descrizione è il contratto; tool_call_id."],
    ["1 min", "Architettura", "Moduli piccoli e separati; LM Studio sull'host, app nel container."],
    ["3 min", "Demo", "Domanda ordinaria, domanda sull'ora con riga [strumento] e log, avvio in Docker."],
    ["2 min", "Test e metodo", "70 test senza modello, prove reali separate, TDD, Superpowers, Conventional Commits."],
    ["1 min", "Risultati e limiti", "12/17 → 12/12, giorno della settimana, ragionamento nascosto, punti aperti."],
], [1.5, 2.8, 13.1])
codice("""
.\\.venv\\Scripts\\Activate.ps1 ; $env:LIVELLO_LOG="INFO" ; python -m assistente
Tu> Qual è la capitale della Francia?    → nessuna riga [strumento]
Tu> Che ore sono adesso a Tokyo?         → riga [strumento] + log di instradamento
Tu> E a Roma?                            → la cronologia fa capire il riferimento
docker compose build ; docker compose run --rm --name assistente-demo -e LIVELLO_LOG=INFO assistente
docker logs -f assistente-demo           (da un secondo terminale) ;  python -m pytest
""")
qa = [
    ("Perché LangGraph e non un ciclo while?",
     "Il flusso diventa esplicito e verificabile: i test controllano quali nodi girano e aggiungere strumenti non richiede di riscrivere il ciclo."),
    ("Il modello esegue l'orologio?",
     "No: produce solo una richiesta (nome + argomenti JSON). La funzione la esegue il nodo strumenti e il risultato torna come ToolMessage."),
    ("Come sapete che l'ora non è inventata?",
     "Riga [strumento] e log con richiesta, esecuzione e risultato; il test reale controlla che la risposta contenga l'HH:MM dello strumento."),
    ("Dove sta la memoria?",
     "Nell'applicazione: Conversazione tiene i messaggi e li reinvia; add_messages aggiunge senza sostituire. Alla chiusura si perde."),
    ("Se LM Studio è spento?",
     "Avviso all'avvio, errore chiaro in chat, sessione aperta e cronologia com'era prima della domanda."),
    ("A che serve il limite di passaggi?",
     "Ferma un modello che chiede lo strumento all'infinito: messaggio esplicito e rollback, nessuna risposta inventata."),
    ("Perché l'ora non dipende dal container?",
     "L'istante si legge in UTC e si converte con zoneinfo + tzdata: il container era in UTC ma lo strumento dava l'ora giusta di Tokyo."),
    ("Come parla il container con LM Studio?",
     "Connessione in uscita verso host.docker.internal:1234; nessuna porta pubblicata, localhost sarebbe il container."),
    ("Come si testa un grafo senza modello?",
     "Modelli finti con risposte prestabilite (testo, tool_calls, eccezioni) e un istante fisso per l'orologio."),
    ("Perché è lento?",
     "Ragionamento nascosto (~90% dei token) a ~16 token/s e due chiamate per le domande sull'ora."),
    ("Come si aggiunge uno strumento?",
     "Un altro BaseTool nella lista strumenti passata a crea_modello e crea_grafo: il nodo lo trova per nome."),
]
h2("Domande probabili: risposte in una riga")
tabella(["Domanda", "Risposta"], [[d, r] for d, r in qa], [5.0, 12.4], stile_prima_colonna="domanda")
riquadro("Prima di iniziare",
         "Avvia LM Studio e carica il modello prima (la prima chiamata è più lenta). Avvisa che ogni risposta richiede "
         "qualche secondo e spiega perché. Tieni aperta una traccia di log già ottenuta, nel caso il modello rallenti.",
         sfondo=VERDE_CHIARO, bordo=VERDE)

doc = SimpleDocTemplate(USCITA, pagesize=A4, leftMargin=MARGINE, rightMargin=MARGINE, topMargin=1.75 * cm,
                        bottomMargin=1.5 * cm, title="Assistente del laboratorio — promemoria per l'esposizione",
                        author="Brandon", subject="Lezione 4 · Dal client a un agente LangGraph")
doc.build(storia, onFirstPage=intestazione_e_piede, onLaterPages=intestazione_e_piede)
if doc.page != PAGINE_ATTESE:
    raise SystemExit(f"Il promemoria ha {doc.page} pagine invece di {PAGINE_ATTESE}: qualche pagina deborda.")
print("scritto", USCITA)
