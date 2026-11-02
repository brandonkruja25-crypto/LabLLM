"""Genera il PDF riassuntivo per l'esposizione dell'assistente del laboratorio.

Non fa parte dell'applicazione: reportlab non è tra le sue dipendenze. Usa i font di Windows
(Segoe UI e Consolas). Da PowerShell, dalla cartella assistente-laboratorio:

    python -m venv $env:TEMP\\pdfenv
    & $env:TEMP\\pdfenv\\Scripts\\python.exe -m pip install reportlab==5.1.0
    & $env:TEMP\\pdfenv\\Scripts\\python.exe docs\\esposizione\\genera_pdf.py docs\\esposizione\\assistente-laboratorio-esposizione.pdf
"""

import sys

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
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
FONT = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Testo", FONT + "segoeui.ttf"))
pdfmetrics.registerFont(TTFont("Testo-B", FONT + "segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Testo-I", FONT + "segoeuii.ttf"))
pdfmetrics.registerFont(TTFont("Codice", FONT + "consola.ttf"))
pdfmetrics.registerFont(TTFont("Codice-B", FONT + "consolab.ttf"))
pdfmetrics.registerFontFamily("Testo", normal="Testo", bold="Testo-B", italic="Testo-I", boldItalic="Testo-B")

BLU = colors.HexColor("#1F3A5F")
BLU_CHIARO = colors.HexColor("#E8EEF6")
ACCENTO = colors.HexColor("#C2622D")
GRIGIO = colors.HexColor("#5A6270")
GRIGIO_CHIARO = colors.HexColor("#F3F4F6")
VERDE = colors.HexColor("#2E7D4F")
VERDE_CHIARO = colors.HexColor("#E7F4EC")
GIALLO_CHIARO = colors.HexColor("#FFF6E0")

S = {
    "titolo": ParagraphStyle("titolo", fontName="Testo-B", fontSize=26, leading=32, textColor=BLU, alignment=TA_CENTER),
    "sottotitolo": ParagraphStyle("sottotitolo", fontName="Testo", fontSize=13, leading=18, textColor=GRIGIO, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="Testo-B", fontSize=17, leading=22, textColor=BLU, spaceBefore=4, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Testo-B", fontSize=12.5, leading=17, textColor=ACCENTO, spaceBefore=10, spaceAfter=4),
    "corpo": ParagraphStyle("corpo", fontName="Testo", fontSize=10, leading=14.5, spaceAfter=5),
    "punto": ParagraphStyle("punto", fontName="Testo", fontSize=10, leading=14, leftIndent=14, bulletIndent=3, spaceAfter=2.5),
    "cella": ParagraphStyle("cella", fontName="Testo", fontSize=8.8, leading=11.5),
    "cella_b": ParagraphStyle("cella_b", fontName="Testo-B", fontSize=8.8, leading=11.5, textColor=colors.white),
    "codice": ParagraphStyle("codice", fontName="Codice", fontSize=8.2, leading=10.6, textColor=colors.HexColor("#1D2430")),
    "riquadro": ParagraphStyle("riquadro", fontName="Testo", fontSize=9.6, leading=13.5),
    "indice": ParagraphStyle("indice", fontName="Testo", fontSize=10.5, leading=17, leftIndent=8),
    "nota": ParagraphStyle("nota", fontName="Testo-I", fontSize=8.8, leading=12, textColor=GRIGIO, spaceAfter=6),
    "domanda": ParagraphStyle("domanda", fontName="Testo-B", fontSize=10, leading=14, textColor=BLU, spaceBefore=6),
}

storia = []


def h1(testo):
    storia.append(CondPageBreak(6 * cm))
    storia.append(Paragraph(testo, S["h1"]))


def h2(testo):
    storia.append(CondPageBreak(3 * cm))
    storia.append(Paragraph(testo, S["h2"]))


def p(testo):
    storia.append(Paragraph(testo, S["corpo"]))


def punti(*voci):
    for voce in voci:
        storia.append(Paragraph(voce, S["punto"], bulletText="•"))
    storia.append(Spacer(1, 3))


def codice(testo, intro=None):
    righe_lunghe = [r for r in testo.strip("\n").splitlines() if len(r) > 99]
    if righe_lunghe:
        raise SystemExit(f"Righe di codice troppo lunghe: {righe_lunghe}")
    blocco = Preformatted(testo.strip("\n"), S["codice"])
    t = Table([[blocco]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIGIO_CHIARO),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D9E0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementi = [t, Spacer(1, 6)]
    if intro:
        elementi.insert(0, Paragraph(intro, S["corpo"]))
    storia.append(KeepTogether(elementi))


def riquadro(titolo, testo, sfondo=BLU_CHIARO, bordo=BLU):
    contenuto = [Paragraph(f"<b>{titolo}</b>", S["riquadro"]), Paragraph(testo, S["riquadro"])]
    t = Table([[contenuto]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), sfondo),
        ("LINEBEFORE", (0, 0), (0, -1), 3, bordo),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    storia.append(KeepTogether([t, Spacer(1, 8)]))


def tabella(intestazione, righe, larghezze):
    dati = [[Paragraph(c, S["cella_b"]) for c in intestazione]]
    dati += [[Paragraph(c, S["cella"]) for c in riga] for riga in righe]
    t = Table(dati, colWidths=[l * cm for l in larghezze], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLU),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIGIO_CHIARO]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD2DC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    storia.append(t)
    storia.append(Spacer(1, 8))


# ---------- diagrammi ----------

def scatola(d, x, y, w, h, testo, sotto="", sfondo=BLU_CHIARO, bordo=BLU, raggio=6, dim=10):
    d.add(Rect(x, y, w, h, rx=raggio, ry=raggio, fillColor=sfondo, strokeColor=bordo, strokeWidth=1.2))
    if sotto:
        d.add(String(x + w / 2, y + h / 2 + 2, testo, fontName="Testo-B", fontSize=dim, fillColor=bordo, textAnchor="middle"))
        d.add(String(x + w / 2, y + h / 2 - 10, sotto, fontName="Testo", fontSize=7.5, fillColor=GRIGIO, textAnchor="middle"))
    else:
        d.add(String(x + w / 2, y + h / 2 - 3.5, testo, fontName="Testo-B", fontSize=dim, fillColor=bordo, textAnchor="middle"))


def freccia(d, x1, y1, x2, y2, colore=GRIGIO, etichetta="", ex=0, ey=0):
    import math
    d.add(Line(x1, y1, x2, y2, strokeColor=colore, strokeWidth=1.3))
    a = math.atan2(y2 - y1, x2 - x1)
    l = 7
    d.add(Polygon([x2, y2, x2 - l * math.cos(a - 0.4), y2 - l * math.sin(a - 0.4),
                   x2 - l * math.cos(a + 0.4), y2 - l * math.sin(a + 0.4)], fillColor=colore, strokeColor=colore))
    if etichetta:
        d.add(String((x1 + x2) / 2 + ex, (y1 + y2) / 2 + ey, etichetta, fontName="Testo-I", fontSize=8, fillColor=colore, textAnchor="middle"))


def diagramma_grafo():
    d = Drawing(465, 215)
    scatola(d, 10, 150, 70, 34, "START", sfondo=colors.white)
    scatola(d, 125, 140, 120, 54, "llm", "messaggi + descrizione strumento")
    rombo_x, rombo_y = 330, 167
    d.add(Polygon([rombo_x, rombo_y + 32, rombo_x + 55, rombo_y, rombo_x, rombo_y - 32, rombo_x - 55, rombo_y],
                  fillColor=GIALLO_CHIARO, strokeColor=ACCENTO, strokeWidth=1.2))
    d.add(String(rombo_x, rombo_y + 3, "instrada()", fontName="Testo-B", fontSize=9, fillColor=ACCENTO, textAnchor="middle"))
    d.add(String(rombo_x, rombo_y - 9, "tool_calls?", fontName="Testo", fontSize=7.5, fillColor=GRIGIO, textAnchor="middle"))
    scatola(d, 405, 150, 55, 34, "END", sfondo=colors.white)
    scatola(d, 270, 20, 120, 54, "strumenti", "esegue ora_corrente", sfondo=VERDE_CHIARO, bordo=VERDE)
    freccia(d, 80, 167, 125, 167)
    freccia(d, 245, 167, 275, 167)
    freccia(d, 385, 167, 405, 167, etichetta="no / limite", ex=-6, ey=16)
    freccia(d, rombo_x, rombo_y - 32, rombo_x, 74, colore=VERDE, etichetta="sì e passaggi < max", ex=48)
    d.add(Line(270, 47, 185, 47, strokeColor=VERDE, strokeWidth=1.3))
    freccia(d, 185, 47, 185, 140, colore=VERDE, etichetta="ToolMessage", ex=-34)
    return d


def diagramma_architettura():
    d = Drawing(465, 270)
    d.add(Rect(5, 40, 330, 225, rx=8, ry=8, fillColor=None, strokeColor=GRIGIO, strokeWidth=1, strokeDashArray=[4, 3]))
    d.add(String(12, 252, "Processo Python (in locale o nel container Docker)", fontName="Testo-I", fontSize=8, fillColor=GRIGIO))
    scatola(d, 20, 175, 130, 44, "terminale", "input / output della chat")
    scatola(d, 185, 175, 135, 44, "conversazione", "cronologia + rollback")
    scatola(d, 185, 110, 135, 44, "grafo", "stato, llm, strumenti")
    scatola(d, 20, 110, 130, 44, "strumenti", "ora_corrente", sfondo=VERDE_CHIARO, bordo=VERDE)
    scatola(d, 185, 50, 135, 44, "modello", "ChatOpenAI + bind_tools")
    scatola(d, 20, 50, 130, 44, "configurazione", "variabili d'ambiente")
    scatola(d, 365, 50, 95, 44, "LM Studio", "sull'host :1234", sfondo=GIALLO_CHIARO, bordo=ACCENTO)
    scatola(d, 365, 175, 95, 44, "utente", "Tu> / Assistente>", sfondo=colors.white)
    d.add(Line(412, 219, 412, 236, strokeColor=GRIGIO, strokeWidth=1.3))
    d.add(Line(412, 236, 85, 236, strokeColor=GRIGIO, strokeWidth=1.3))
    freccia(d, 85, 236, 85, 219)
    d.add(String(250, 240, "domande e risposte", fontName="Testo-I", fontSize=8, fillColor=GRIGIO, textAnchor="middle"))
    freccia(d, 150, 197, 185, 197)
    freccia(d, 252, 175, 252, 154)
    freccia(d, 185, 132, 150, 132, etichetta="invoke", ey=4)
    freccia(d, 252, 110, 252, 94)
    freccia(d, 320, 72, 365, 72, colore=ACCENTO, etichetta="HTTP /v1", ey=5)
    freccia(d, 150, 72, 185, 72)
    d.add(String(232, 20, "__main__ legge la configurazione, crea strumento, modello, grafo e conversazione, poi avvia la chat",
                 fontName="Testo-I", fontSize=8, fillColor=GRIGIO, textAnchor="middle"))
    return d


def diagramma_docker():
    d = Drawing(465, 150)
    d.add(Rect(5, 10, 455, 135, rx=8, ry=8, fillColor=GRIGIO_CHIARO, strokeColor=GRIGIO, strokeWidth=1))
    d.add(String(14, 130, "Computer host (Windows)", fontName="Testo-B", fontSize=9, fillColor=GRIGIO))
    d.add(Rect(20, 25, 230, 95, rx=6, ry=6, fillColor=BLU_CHIARO, strokeColor=BLU, strokeWidth=1.2))
    d.add(String(30, 105, "Docker Desktop · container «assistente»", fontName="Testo-B", fontSize=8.5, fillColor=BLU))
    for i, riga in enumerate(["python:3.13-slim + dipendenze", "grafo, terminale, strumento orologio",
                              "LMSTUDIO_BASE_URL =", "http://host.docker.internal:1234/v1"]):
        d.add(String(30, 88 - i * 14, riga, fontName="Codice" if i >= 2 else "Testo", fontSize=8, fillColor=colors.black))
    scatola(d, 330, 50, 115, 50, "LM Studio", "google/gemma-4-e2b", sfondo=GIALLO_CHIARO, bordo=ACCENTO)
    freccia(d, 250, 82, 330, 82, colore=ACCENTO, etichetta="richiesta", ey=5)
    freccia(d, 330, 64, 250, 64, colore=ACCENTO, etichetta="risposta", ey=-12)
    d.add(String(232, 14, "Connessione in uscita: nessuna porta pubblicata. Nel container «localhost» è il container stesso.",
                 fontName="Testo-I", fontSize=7.5, fillColor=GRIGIO, textAnchor="middle"))
    return d


# ---------- pagine ----------

def piede(canvas, doc):
    canvas.saveState()
    canvas.setFont("Testo", 8)
    canvas.setFillColor(GRIGIO)
    canvas.drawString(2.3 * cm, 1.3 * cm, "Assistente del laboratorio · guida per l'esposizione")
    canvas.drawRightString(A4[0] - 2.3 * cm, 1.3 * cm, f"pagina {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#D5D9E0"))
    canvas.line(2.3 * cm, 1.65 * cm, A4[0] - 2.3 * cm, 1.65 * cm)
    canvas.restoreState()


def copertina(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLU)
    canvas.rect(0, A4[1] - 5 * cm, A4[0], 5 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Testo", 10)
    canvas.drawCentredString(A4[0] / 2, A4[1] - 2.2 * cm, "DEEP LEARNING E LLM: COSTRUIRE CHATBOT E AGENTI · ITS ALTO ADRIATICO")
    canvas.setFont("Testo-B", 12)
    canvas.drawCentredString(A4[0] / 2, A4[1] - 3.1 * cm, "Lezione 4 · Dal client a un agente LangGraph")
    canvas.restoreState()


storia.append(Spacer(1, 4.6 * cm))
storia.append(Paragraph("Assistente del laboratorio", S["titolo"]))
storia.append(Spacer(1, 8))
storia.append(Paragraph("Chatbot da terminale con grafo LangGraph, modello locale in LM Studio,<br/>"
                        "strumento orologio e avvio con Docker Compose", S["sottotitolo"]))
storia.append(Spacer(1, 22))
storia.append(Paragraph("Guida riassuntiva e teorica per preparare l'esposizione", S["sottotitolo"]))
storia.append(Spacer(1, 40))
tabella(["Dato", "Valore"], [
    ["Progetto", "<font name='Codice'>Lezione 4/assistente-laboratorio/</font>, branch <font name='Codice'>main</font>"],
    ["Repository", "<font name='Codice'>github.com/brandonkruja25-crypto/LabLLM</font> · branch <font name='Codice'>main</font> pubblicato su origin"],
    ["Modello", "<font name='Codice'>google/gemma-4-e2b</font> (GGUF, Q4_K_M) servito da LM Studio sull'host"],
    ["Tecnologie", "Python 3.13 · LangGraph 1.2.18 · langchain-openai 1.7.3 · Docker Compose v5"],
    ["Test", "70 automatici senza modello · 3 prove reali LM Studio · 1 prova reale Docker"],
    ["Data", "2 novembre 2026"],
], [4, 12.4])
storia.append(PageBreak())

storia.append(Paragraph("Indice", S["h1"]))
for voce in [
    "1. Il progetto in breve",
    "2. Teoria · LLM locali, LM Studio e API compatibile con OpenAI",
    "3. Teoria · LangGraph: stato, nodi, archi e cicli",
    "4. Teoria · Tool calling: il modello chiede, il programma esegue",
    "5. Teoria · Tempo, fusi orari IANA e ISO 8601",
    "6. Teoria · Docker e Docker Compose",
    "7. Architettura del progetto",
    "8. Il grafo nel dettaglio",
    "9. Un turno passo per passo",
    "10. Lo strumento orologio",
    "11. Cronologia, rollback ed errori",
    "12. Configurazione",
    "13. Test e verifiche",
    "14. Metodo di lavoro: CLAUDE.md, Superpowers e Git",
    "15. Risultati, misure e decisioni",
    "16. Limiti, problemi aperti e prossimi passi",
    "17. Come impostare l'esposizione (scaletta e demo)",
    "18. Domande probabili e risposte",
    "19. Glossario",
]:
    storia.append(Paragraph(voce, S["indice"]))
storia.append(PageBreak())

# 1
h1("1. Il progetto in breve")
p("L'<b>assistente del laboratorio</b> è un'applicazione Python da terminale che conversa con un modello "
  "linguistico eseguito in locale da <b>LM Studio</b>. Il flusso dell'applicazione non è scritto in modo lineare: è "
  "descritto da un <b>grafo LangGraph</b> esplicito, con uno stato condiviso, dei nodi e una funzione di instradamento. "
  "Quando l'utente chiede l'ora, il modello non la inventa: <b>richiede lo strumento orologio</b>, il programma lo "
  "esegue davvero e il risultato torna al modello, che formula la risposta finale.")
punti(
    "<b>Grafo esplicito</b>: START → llm → (strumenti → llm)* → END, con limite di passaggi per turno.",
    "<b>Cronologia di sessione</b>: il modello riceve a ogni turno tutta la conversazione; alla chiusura viene persa.",
    "<b>Strumento orologio</b> <font name='Codice'>ora_corrente(fuso_orario?)</font> con fuso IANA esplicito, visibile in chat e nei log.",
    "<b>Docker Compose</b>: l'applicazione gira nel container, LM Studio resta sull'host.",
    "<b>Test</b> automatici indipendenti dal modello e <b>prove reali</b> separate, attivate esplicitamente.",
)
codice("""
Assistente del laboratorio — modello google/gemma-4-e2b su http://localhost:1234/v1
Scrivi «esci» per terminare.
Tu> Che ore sono adesso a Tokyo?
[strumento] ora_corrente(fuso_orario="Asia/Tokyo")
            → 2026-10-28T20:08:51+09:00 (Asia/Tokyo), mercoledì
Assistente> Adesso sono le 20:08:51 di mercoledì 28 ottobre 2026 a Tokyo.
Tu> Che giorno della settimana è oggi a New York?
[strumento] ora_corrente(fuso_orario="America/New_York")
            → 2026-10-28T07:09:08-04:00 (America/New_York), mercoledì
Assistente> Oggi a New York è mercoledì.
Tu> esci
""", intro="Esempio reale di sessione (28 ottobre 2026; le righe [strumento] sono mandate a capo qui per "
           "leggibilità, nel terminale sono su una riga sola):")
h2("Requisiti obbligatori della consegna (slide 26) e stato")
tabella(["Requisito", "Evidenza", "Stato"], [
    ["Grafo con LLM e cronologia", "Conversazione su più turni: al secondo turno il modello ricorda «Ada»", "Fatto"],
    ["Strumento orologio", "Richiesta, esecuzione e risultato nella riga [strumento] e nei log INFO", "Fatto"],
    ["Docker Compose", "Container collegato a LM Studio; prova -m docker superata; chat interattiva provata a mano", "Fatto"],
    ["Test", "70 automatici + prove reali con marcatori lmstudio e docker", "Fatto"],
    ["Documentazione", "README, .env.example e CLAUDE.md coerenti; guida all'avvio AVVIO.md", "Fatto"],
    ["Repository condivisa", "Commit Conventional leggibili; push su origin/main", "Fatto"],
], [4, 8.4, 4])

# 2
h1("2. Teoria · LLM locali, LM Studio e API compatibile con OpenAI")
h2("Che cosa fa un LLM")
p("Un <b>Large Language Model</b> è una rete neurale (un Transformer) addestrata a prevedere il <b>token successivo</b> "
  "di un testo. Un token è un frammento di parola. Generare una risposta significa ripetere la previsione token dopo token "
  "finché il modello produce un segnale di fine. Da questo derivano tre proprietà che guidano tutto il progetto:")
punti(
    "<b>Il modello è senza stato</b>: ogni chiamata è indipendente. Se vogliamo che «ricordi» la conversazione, "
    "dobbiamo rinviargli ogni volta la cronologia. La «memoria» è dell'applicazione, non del modello.",
    "<b>Il modello non ha accesso al mondo</b>: non legge l'orologio, non apre file, non naviga. Può solo produrre testo "
    "plausibile. Per un dato corrente come l'ora serve uno <b>strumento</b> eseguito dal programma.",
    "<b>Il modello è probabilistico</b>: la stessa domanda può dare risposte diverse. Per questo le prove reali vanno "
    "ripetute e i risultati riportati con la loro frequenza (es. 12 su 12).",
)
h2("LM Studio")
p("LM Studio è un'applicazione desktop che scarica ed esegue modelli in formato <b>GGUF</b> sul computer locale e li "
  "espone tramite un server HTTP con un'<b>API compatibile con OpenAI</b>, di default su "
  "<font name='Codice'>http://localhost:1234/v1</font>. Gli endpoint usati dal progetto sono due:")
tabella(["Endpoint", "Uso nel progetto"], [
    ["<font name='Codice'>GET /v1/models</font>", "All'avvio: verificare che <font name='Codice'>LMSTUDIO_MODEL</font> esista davvero. L'identificativo del modello non si inventa: è quello restituito qui."],
    ["<font name='Codice'>POST /v1/chat/completions</font>", "A ogni passaggio del nodo llm: invio di messaggi e descrizione degli strumenti, ricezione della risposta o delle richieste di tool."],
], [5.2, 11.2])
p("Poiché l'API è compatibile con OpenAI, il progetto usa il client standard <b>ChatOpenAI</b> di langchain-openai "
  "cambiando solo <font name='Codice'>base_url</font>. LM Studio non richiede una chiave: il codice usa il segnaposto fisso "
  "<font name='Codice'>\"lm-studio\"</font>, che non è una credenziale.")
h2("Messaggi e ruoli")
tabella(["Ruolo", "Classe LangChain", "Contenuto"], [
    ["system", "SystemMessage", "Istruzioni stabili: rispondi in italiano, per data e ora usa sempre ora_corrente, passa il fuso IANA del luogo."],
    ["user", "HumanMessage", "La domanda dell'utente."],
    ["assistant", "AIMessage", "La risposta del modello, oppure una o più richieste di strumento (tool_calls) con id."],
    ["tool", "ToolMessage", "Il risultato dello strumento, collegato alla richiesta tramite tool_call_id."],
], [2.3, 3.4, 10.7])
h2("Il modello usato")
p("<font name='Codice'>google/gemma-4-e2b</font> è una variante piccola di Gemma 4 (circa 2 miliardi di parametri "
  "effettivi), quantizzata <b>Q4_K_M</b>: i pesi sono memorizzati con circa 4 bit invece di 16, così il modello occupa "
  "meno memoria e gira su un PC, con una piccola perdita di qualità. In LM Studio è caricato con un contesto di "
  "8192 token e dichiara la capacità <i>tool_use</i>.")
riquadro("Da sapere: il modello «pensa» prima di rispondere",
         "Le misure hanno mostrato che Gemma 4 lavora in modalità <i>thinking</i>: prima della risposta genera un "
         "ragionamento nascosto (in inglese) di circa 140–195 token, cioè circa il 90% dei token generati. "
         "A circa 16 token al secondo è la causa principale dell'attesa (vedi sezione 15).",
         sfondo=GIALLO_CHIARO, bordo=ACCENTO)

# 3
h1("3. Teoria · LangGraph: stato, nodi, archi e cicli")
p("In un client semplice il percorso è scritto direttamente nel codice: leggi la domanda, chiama il modello, stampa. "
  "Con <b>LangGraph</b> le operazioni e i passaggi vengono descritti come un <b>grafo</b>, che può avere percorsi "
  "alternativi e cicli. La chiamata al modello diventa <i>un'operazione</i> del programma, non l'intera applicazione. "
  "LM Studio continua a eseguire il modello; LangGraph gestisce il flusso dell'applicazione Python.")
tabella(["Elemento", "Significato", "Nel progetto"], [
    ["Stato", "Dati condivisi durante l'esecuzione (un TypedDict)", "<font name='Codice'>messages</font>, <font name='Codice'>passaggi</font>, <font name='Codice'>limite_raggiunto</font>"],
    ["Nodo", "Funzione che legge lo stato e restituisce un aggiornamento parziale", "<font name='Codice'>llm</font> e <font name='Codice'>strumenti</font>"],
    ["Arco", "Collegamento fisso tra due nodi", "START → llm, strumenti → llm"],
    ["Arco condizionale", "Una funzione sceglie il nodo successivo in base allo stato", "<font name='Codice'>instrada()</font>: «strumenti» oppure «fine»"],
    ["START / END", "Ingresso e uscita del grafo", "L'uscita restituisce lo stato finale al chiamante"],
    ["Reducer", "Regola con cui un aggiornamento si combina con lo stato", "<font name='Codice'>add_messages</font>: aggiunge i messaggi invece di sostituire la lista"],
], [3.2, 6.6, 6.6])
h2("Il ciclo di vita di un grafo")
punti(
    "<b>Definire lo stato</b>: quali dati attraversano il grafo.",
    "<b>Registrare i nodi</b>: <font name='Codice'>add_node(\"llm\", funzione)</font>.",
    "<b>Collegare i nodi</b>: <font name='Codice'>add_edge</font> e <font name='Codice'>add_conditional_edges</font>.",
    "<b>Compilare</b>: <font name='Codice'>compile()</font> produce un grafo eseguibile. La compilazione non chiama il "
    "modello e non dimostra che il comportamento sia corretto.",
    "<b>Invocare</b>: <font name='Codice'>invoke(stato_iniziale)</font> restituisce lo stato finale; "
    "<font name='Codice'>stream(..., stream_mode=\"updates\")</font> mostra quali nodi sono stati eseguiti (usato nei test).",
)
h2("Il reducer add_messages")
p("Un nodo restituisce solo i campi che cambia. Per la maggior parte dei campi il nuovo valore sostituisce il vecchio "
  "(per esempio <font name='Codice'>passaggi</font>). Per <font name='Codice'>messages</font> invece il reducer "
  "<font name='Codice'>add_messages</font> <b>aggiunge</b> i nuovi messaggi in coda (o aggiorna quelli con lo stesso id). "
  "Senza questo reducer, il nodo llm cancellerebbe per errore tutta la cronologia scrivendo solo la sua risposta.")
h2("Dal chatbot all'agente: il ciclo con strumenti")
p("Un grafo con un arco che torna indietro (strumenti → llm) è un <b>ciclo</b>: il modello può chiedere uno strumento, "
  "ricevere il risultato e decidere se chiederne un altro o rispondere. È lo schema di base degli <b>agenti</b>. "
  "Ogni ciclo deve avere una condizione di uscita: qui la fine arriva quando il modello non chiede più strumenti, "
  "oppure quando si raggiunge <font name='Codice'>MAX_PASSAGGI</font> chiamate al modello nello stesso turno.")
storia.append(KeepTogether([diagramma_grafo(), Paragraph("Figura 1 · Il grafo dell'assistente. La funzione di "
              "instradamento è scritta nel progetto (non è il condizionale precostruito di LangGraph), così la "
              "decisione è leggibile e registrata nei log.", S["nota"])]))

# 4
h1("4. Teoria · Tool calling: il modello chiede, il programma esegue")
p("Il <b>tool calling</b> (o function calling) permette a un modello di usare funzioni del programma. Il punto chiave "
  "per l'esposizione: <b>il modello non esegue nulla</b>. Produce soltanto una richiesta strutturata; l'esecuzione "
  "avviene nel codice Python.")
tabella(["Passo", "Chi", "Che cosa succede"], [
    ["1", "Programma", "Invia al modello i messaggi e, nel campo <font name='Codice'>tools</font>, la descrizione dello strumento in JSON Schema: nome, descrizione, parametri."],
    ["2", "Modello", "Se serve, risponde con <font name='Codice'>tool_calls</font>: nome dello strumento, argomenti in JSON e un id univoco (es. call_1)."],
    ["3", "Programma", "Il nodo strumenti esegue la funzione reale e aggiunge un ToolMessage con lo stesso <font name='Codice'>tool_call_id</font>."],
    ["4", "Modello", "Riceve il risultato associato alla sua richiesta e formula la risposta finale (o chiede un altro strumento)."],
], [1.2, 2.4, 12.8])
codice("""
{"type": "function",
 "function": {
   "name": "ora_corrente",
   "description": "Restituisce la data, l'ora e il giorno della settimana attuali.
       Usala ogni volta che servono data, ora o giorno correnti, senza inventarli.
       Il parametro fuso_orario è un nome di fuso IANA, per esempio Europe/Rome,
       Asia/Tokyo, America/New_York, UTC. ...",
   "parameters": {
     "type": "object",
     "properties": {
       "fuso_orario": {
         "anyOf": [{"type": "string"}, {"type": "null"}],
         "default": null,
         "description": "nome di fuso IANA del luogo di cui si chiede l'ora, per esempio
             Asia/Tokyo per Tokyo ... Indicalo sempre quando la domanda nomina una città
             o un paese; omettilo solo per l'ora locale."}}}}}
""", intro="Lo schema che il modello riceve davvero per l'orologio (generato da LangChain a partire dalla "
           "funzione Python):")
h2("Perché la descrizione conta")
p("La descrizione è l'unica cosa che il modello sa dello strumento: è il suo <b>contratto</b>. Nel progetto l'abbiamo "
  "misurato: senza la descrizione del parametro, alla domanda sull'ora a Tokyo il modello ometteva "
  "<font name='Codice'>fuso_orario</font> in 5 casi su 17 (e otteneva l'ora di Roma); con la descrizione del parametro "
  "e una frase nel prompt di sistema la prova è passata 12 volte su 12.")
h2("Casi difficili gestiti")
punti(
    "<b>Strumento inesistente</b> (es. «meteo»): ToolMessage che inizia con <font name='Codice'>Errore:</font>, il turno prosegue.",
    "<b>Argomenti sconosciuti</b> (es. <font name='Codice'>{\"timezone\": \"Asia/Tokyo\"}</font>): lo schema pydantic li "
    "ignorerebbe in silenzio e lo strumento darebbe l'ora di Roma. Il nodo li confronta con quelli ammessi e restituisce un errore.",
    "<b>Argomenti che non sono JSON valido</b>: LangChain li mette in <font name='Codice'>invalid_tool_calls</font>. "
    "Il nodo produce comunque un ToolMessage di errore, così in cronologia non resta una richiesta senza risposta.",
    "<b>Eccezione nello strumento</b>: intercettata e trasformata in testo di errore per il modello, senza crash.",
)
riquadro("Principio di verifica",
         "Una risposta plausibile sull'ora <b>non</b> dimostra che lo strumento sia stato usato. Servono le evidenze "
         "nella traccia: richiesta del modello con nome e argomenti, esecuzione della funzione, risultato, ritorno al "
         "modello associato al tool_call_id corretto, risposta che usa quel dato. E va confrontato con una domanda "
         "ordinaria, che non deve usare lo strumento.")

# 5
h1("5. Teoria · Tempo, fusi orari IANA e ISO 8601")
punti(
    "<b>UTC</b> è il riferimento universale. Un'ora senza fuso o offset è ambigua: «13:00» dove?",
    "<b>Offset</b>: differenza da UTC, per esempio <font name='Codice'>+09:00</font> per Tokyo.",
    "<b>Fuso IANA</b>: nome standard nel formato Area/Città (<font name='Codice'>Europe/Rome</font>, "
    "<font name='Codice'>Asia/Tokyo</font>, <font name='Codice'>America/New_York</font>, <font name='Codice'>UTC</font>). "
    "A differenza di un offset fisso, conosce la storia delle regole e l'<b>ora legale</b>: Roma è +01:00 in inverno e +02:00 in estate.",
    "<b>ISO 8601</b>: formato standard di data e ora, es. <font name='Codice'>2026-10-28T20:08:51+09:00</font>.",
    "<b>zoneinfo</b> è il modulo della libreria standard Python per i fusi IANA; il pacchetto <b>tzdata</b> fornisce "
    "il database dei fusi dove il sistema non lo ha (Windows e l'immagine <font name='Codice'>python:3.13-slim</font>).",
)
p("Regola di progetto: l'istante si legge <b>sempre in UTC</b> e si converte nel fuso richiesto. Il fuso del computer "
  "o del container non influisce. È stato verificato: i log del container erano in UTC (10:25) mentre lo strumento "
  "restituiva correttamente le 19:25 di Tokyo.")
p("Anche il <b>giorno della settimana</b> viene calcolato nel fuso richiesto (alle 20:00 UTC di giovedì a Tokyo è "
  "già venerdì) e preso da una tabella di nomi italiani: <font name='Codice'>strftime(\"%A\")</font> dipenderebbe dalle "
  "impostazioni di lingua del sistema.")

# 6
h1("6. Teoria · Docker e Docker Compose")
tabella(["Concetto", "Significato"], [
    ["Immagine", "Pacchetto immutabile con applicazione, runtime Python e dipendenze, costruito da un Dockerfile a strati (layer)."],
    ["Container", "Istanza in esecuzione di un'immagine, con processo, configurazione e stato propri."],
    ["Dockerfile", "Ricetta per costruire l'immagine."],
    ["compose.yaml", "Descrive come eseguire l'applicazione: servizi, build, variabili, rete. Rende l'avvio ripetibile anche con un solo servizio."],
    [".dockerignore", "Esclude file dal contesto di build: qui .env (segreti), .venv, cache, .git, tests e docs."],
    ["Cache dei layer", "Il Dockerfile copia prima requirements.txt e installa, poi copia il codice: se cambia solo il codice, le dipendenze non vengono reinstallate."],
], [3.4, 13])
codice("""
# Dockerfile
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY assistente/ assistente/
CMD ["python", "-m", "assistente"]
""")
codice("""
# compose.yaml
services:
  assistente:
    build: .
    env_file: .env
    environment:
      LMSTUDIO_BASE_URL: http://host.docker.internal:1234/v1
    extra_hosts:
      - "host.docker.internal:host-gateway"
    stdin_open: true    # come -i
    tty: true           # come -t
""")
punti(
    "<font name='Codice'>PYTHONUNBUFFERED=1</font>: output e log escono subito, così <font name='Codice'>docker logs -f</font> li mostra in tempo reale.",
    "<font name='Codice'>environment</font> prevale su <font name='Codice'>env_file</font>: nel container l'indirizzo di LM Studio è sempre quello dell'host.",
    "<font name='Codice'>stdin_open</font> e <font name='Codice'>tty</font> servono alla chat interattiva; per una CLI si usa "
    "<font name='Codice'>docker compose run</font> e non <font name='Codice'>up</font>.",
)
storia.append(KeepTogether([diagramma_docker(), Paragraph("Figura 2 · L'applicazione nel container, LM Studio "
              "sull'host. host.docker.internal è il nome con cui Docker Desktop permette al container di raggiungere il computer host.", S["nota"])]))
tabella(["Comando", "A che cosa serve"], [
    ["<font name='Codice'>docker compose build</font>", "Costruisce l'immagine (da rifare dopo ogni modifica al codice)."],
    ["<font name='Codice'>docker compose run --rm --name assistente-demo assistente</font>", "Avvia la chat collegata al terminale; --rm rimuove il container all'uscita."],
    ["<font name='Codice'>docker ps</font>", "Elenca i container attivi (da un secondo terminale)."],
    ["<font name='Codice'>docker logs -f assistente-demo</font>", "Segue l'output e i log del container."],
    ["<font name='Codice'>... run --rm -T assistente</font>", "Senza TTY: permette di passare l'input da pipe (usato nella prova automatica)."],
], [7.6, 8.8])

# 7
h1("7. Architettura del progetto")
p("Il codice è diviso in moduli piccoli, ciascuno con una responsabilità (467 righe in tutto). Le lezioni successive "
  "estenderanno questo codice senza ripartire da zero: per esempio, un nuovo strumento si aggiunge alla lista "
  "<font name='Codice'>strumenti</font> passata a modello e grafo.")
storia.append(KeepTogether([diagramma_architettura(), Paragraph("Figura 3 · Moduli e dipendenze.", S["nota"])]))
tabella(["Modulo", "Responsabilità"], [
    ["<font name='Codice'>configurazione.py</font>", "Legge e valida le variabili d'ambiente; errore chiaro che nomina la variabile."],
    ["<font name='Codice'>strumenti.py</font>", "Strumento <font name='Codice'>ora_corrente</font>, validazione dei fusi, formato del risultato."],
    ["<font name='Codice'>modello.py</font>", "ChatOpenAI verso LM Studio con <font name='Codice'>bind_tools</font>; controllo di GET /v1/models."],
    ["<font name='Codice'>grafo.py</font>", "Stato, nodi llm e strumenti, <font name='Codice'>instrada</font>, limite di passaggi, log."],
    ["<font name='Codice'>conversazione.py</font>", "Cronologia di sessione, rollback del turno, chiamate allo strumento del turno, errori del modello."],
    ["<font name='Codice'>terminale.py</font>", "Ciclo Tu&gt; / Assistente&gt;, righe [strumento], uscita pulita."],
    ["<font name='Codice'>__main__.py</font>", "Avvio: .env, configurazione, log su stderr, verifica del modello, composizione dei pezzi."],
], [4.2, 12.2])
h2("Dipendenze (versioni fissate)")
tabella(["Pacchetto", "Motivo"], [
    ["langgraph 1.2.18", "Grafo esplicito con stato, nodi e instradamento."],
    ["langchain-core 1.7.0", "Messaggi, strumenti, interfaccia Runnable."],
    ["langchain-openai 1.7.3", "ChatOpenAI, client compatibile con l'API di LM Studio."],
    ["openai 3.39.0", "SDK usato da langchain-openai; fissato per riconoscerne gli errori (APIError)."],
    ["python-dotenv 1.2.4", "Carica .env nell'esecuzione locale."],
    ["tzdata 2026.5", "Database dei fusi IANA, assente nell'immagine slim e su Windows."],
    ["pytest 9.1.1 (solo sviluppo)", "Test automatici e prove reali con marcatori."],
], [4.6, 11.8])

# 8
h1("8. Il grafo nel dettaglio")
codice("""
class StatoConversazione(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]   # si aggiunge, non si sostituisce
    passaggi: int                                         # chiamate al nodo llm nel turno
    limite_raggiunto: bool

def instrada(stato, max_passaggi) -> Literal["strumenti", "fine"]:
    if not _richieste_di_tool(stato):    # richieste di tool dell'ultimo messaggio
        log.info("Instradamento: risposta finale → fine")
        return "fine"
    if stato.get("passaggi", 0) >= max_passaggi:
        log.info("Instradamento: strumento richiesto ma limite di passaggi raggiunto → fine")
        return "fine"
    log.info("Instradamento: il modello chiede uno strumento → strumenti")
    return "strumenti"

costruttore = StateGraph(StatoConversazione)
costruttore.add_node("llm", llm)
costruttore.add_node("strumenti", nodo_strumenti)
costruttore.add_edge(START, "llm")
costruttore.add_conditional_edges("llm", lambda stato: instrada(stato, max_passaggi),
                                  {"strumenti": "strumenti", "fine": END})
costruttore.add_edge("strumenti", "llm")
grafo = costruttore.compile()
""")
tabella(["Nodo", "Che cosa fa"], [
    ["llm", "Incrementa <font name='Codice'>passaggi</font>; invia al modello [SystemMessage(prompt), *messaggi]; registra a INFO inizio, fine e durata; "
            "se il modello chiede ancora uno strumento all'ultimo passaggio consentito imposta <font name='Codice'>limite_raggiunto</font> e registra un WARNING."],
    ["strumenti", "Per ogni richiesta dell'ultimo messaggio cerca lo strumento per nome, controlla gli argomenti, lo esegue "
                  "e aggiunge un ToolMessage con il tool_call_id della richiesta; registra a INFO richiesta e risultato."],
], [2.6, 13.8])
h2("Il limite di passaggi")
p("Con <font name='Codice'>MAX_PASSAGGI=3</font> e un modello che chiede sempre lo strumento, il grafo esegue "
  "llm 3 volte e strumenti 2 volte, poi si ferma con <font name='Codice'>limite_raggiunto=True</font>. La chat mostra "
  "«Limite di passaggi raggiunto: nessuna risposta finale. Riformula la domanda.»: l'applicazione non inventa una risposta. "
  "Il valore predefinito è 6.")
riquadro("Scelta progettuale: niente checkpointer",
         "LangGraph può salvare lo stato tra un'invocazione e l'altra con un checkpointer. Qui il grafo è compilato "
         "senza: la cronologia vive nell'oggetto Conversazione ed entra nel grafo a ogni turno. Così il rollback di "
         "un turno fallito è semplice (si scarta il risultato) e la persistenza, esclusa dai requisiti, non c'è.")

# 9
h1("9. Un turno passo per passo")
p("Domanda: «Che ore sono adesso a Tokyo?». Messaggi nello stato alla fine del turno:")
tabella(["#", "Messaggio", "Prodotto da", "Contenuto"], [
    ["1", "HumanMessage", "Conversazione", "Che ore sono adesso a Tokyo?"],
    ["2", "AIMessage", "nodo llm (passaggio 1)", "contenuto vuoto + tool_calls: ora_corrente({\"fuso_orario\": \"Asia/Tokyo\"}), id call_…"],
    ["3", "ToolMessage", "nodo strumenti", "2026-10-28T20:08:51+09:00 (Asia/Tokyo), mercoledì · tool_call_id = id della richiesta"],
    ["4", "AIMessage", "nodo llm (passaggio 2)", "Adesso sono le 20:08:51 di mercoledì 28 ottobre 2026 a Tokyo."],
], [0.7, 2.8, 3.6, 9.3])
p("Log reali con <font name='Codice'>LIVELLO_LOG=INFO</font> (prova del 28 ottobre, prima dell'aggiunta del giorno della settimana):")
codice("""
11:20:13 INFO assistente.grafo: Inizio chiamata al modello (passaggio 1, 1 messaggi)
11:20:21 INFO assistente.grafo: Fine chiamata al modello in 7.78 s
11:20:21 INFO assistente.grafo: Instradamento: il modello chiede uno strumento → strumenti
11:20:21 INFO assistente.grafo: Richiesta di strumento: ora_corrente({'fuso_orario': 'Asia/Tokyo'})
11:20:21 INFO assistente.grafo: Risultato di ora_corrente: 2026-10-28T19:20:21+09:00 (Asia/Tokyo)
11:20:21 INFO assistente.grafo: Inizio chiamata al modello (passaggio 2, 3 messaggi)
11:20:31 INFO assistente.grafo: Fine chiamata al modello in 9.74 s
11:20:31 INFO assistente.grafo: Instradamento: risposta finale → fine
""")
p("Questa traccia contiene tutte le evidenze richieste dalla slide 13: richiesta del modello (nome e argomenti), "
  "esecuzione, risultato, ritorno al modello e risposta che usa il dato. Alla domanda successiva «E a Roma?» il modello "
  "ha passato <font name='Codice'>Europe/Rome</font>: ha capito il riferimento grazie alla cronologia.")

# 10
h1("10. Lo strumento orologio")
tabella(["Parte del contratto", "Decisione"], [
    ["Nome", "<font name='Codice'>ora_corrente</font>"],
    ["Descrizione", "Restituisce data, ora e giorno della settimana attuali; da usare ogni volta che servono, senza inventarli; esempi di fusi IANA."],
    ["Parametro", "<font name='Codice'>fuso_orario</font> facoltativo, nome IANA; spazi esterni rimossi. Se assente: <font name='Codice'>FUSO_ORARIO_PREDEFINITO</font> (Europe/Rome)."],
    ["Risultato", "<font name='Codice'>AAAA-MM-GGTHH:MM:SS±HH:MM (Nome/IANA), giorno</font> · es. <font name='Codice'>2026-01-15T13:00:00+01:00 (Europe/Rome), giovedì</font>"],
    ["Errori", "Nessuna eccezione: testo che inizia con <font name='Codice'>Errore:</font>, con il valore ricevuto e un esempio IANA (Asia/Tokyo)."],
], [3.6, 12.8])
codice("""
def ora_corrente_testo(fuso_orario, fuso_predefinito, adesso_utc: datetime) -> str:
    richiesto = fuso_predefinito if fuso_orario is None else fuso_orario
    try:
        zona = valida_fuso(richiesto)      # ZoneInfo, oppure ValueError
    except ValueError:
        return (f"Errore: fuso orario non riconosciuto: {richiesto!r}. "
                f"Usa un nome di fuso IANA, per esempio Asia/Tokyo ({ESEMPI_FUSO}).")
    locale = adesso_utc.astimezone(zona)
    return f"{locale.isoformat(timespec='seconds')} ({zona.key}), {GIORNI[locale.weekday()]}"
""")
p("L'istante è un parametro: in produzione arriva da <font name='Codice'>datetime.now(timezone.utc)</font>, nei test è "
  "un istante fisso. Così i test confrontano valori stabili (Roma in inverno +01:00 e in estate +02:00, Tokyo, UTC, "
  "cambio di giorno tra UTC e Tokyo). Valori rifiutati senza eccezioni: <font name='Codice'>Tokyo</font>, "
  "<font name='Codice'>UTC+2</font>, stringa vuota, <font name='Codice'>../etc/passwd</font>, <font name='Codice'>Europe</font>.")

# 11
h1("11. Cronologia, rollback ed errori")
p("La classe <b>Conversazione</b> conserva la cronologia della sessione. A ogni turno invoca il grafo con "
  "<font name='Codice'>[*cronologia, HumanMessage(testo)]</font>, <font name='Codice'>passaggi=0</font> e "
  "<font name='Codice'>limite_raggiunto=False</font>. La cronologia viene sostituita con i messaggi restituiti "
  "<b>solo se il turno riesce</b>.")
riquadro("Rollback completo del turno",
         "Se il modello non risponde o si raggiunge il limite di passaggi, la cronologia torna esattamente com'era prima "
         "della domanda: né la domanda, né richieste di tool rimaste senza risposta, né risultati parziali. Così la "
         "richiesta successiva a LM Studio è sempre valida e l'utente può riformulare.", sfondo=VERDE_CHIARO, bordo=VERDE)
tabella(["Situazione", "Comportamento (verificato)"], [
    ["LM Studio non raggiungibile all'avvio", "Avviso con l'indirizzo provato; la chat si apre comunque."],
    ["LM Studio non raggiungibile durante la chat", "Errore: Impossibile contattare il modello su … Controlla che LM Studio sia avviato…; sessione aperta, cronologia invariata."],
    ["Errore HTTP del server (es. modello scaricato)", "Stesso messaggio chiaro e stesso rollback (openai.APIError copre entrambi i casi)."],
    ["Modello configurato inesistente", "Uscita con codice 1 e l'elenco degli identificativi disponibili."],
    ["Configurazione mancante o non valida", "Uscita con codice 1 e messaggio che nomina la variabile, senza traceback."],
    ["Risposta vuota del modello", "Assistente&gt; (il modello non ha restituito testo)"],
    ["Limite di passaggi", "Messaggio esplicito, nessuna risposta inventata, rollback."],
    ["Ctrl+C, fine input, esci", "Uscita pulita senza traceback, anche durante l'attesa della risposta o all'avvio (codice 130)."],
    ["Output rediretto su file (Windows)", "Nessun crash: i caratteri non codificabili diventano «?»."],
    ["Input passato con una pipe in PowerShell", "Il BOM che PowerShell antepone al testo viene ignorato: «esci» chiude la chat."],
], [5.6, 10.8])

# 12
h1("12. Configurazione")
p("La configurazione arriva solo da variabili d'ambiente. In locale si usa il file <font name='Codice'>.env</font>, "
  "escluso da Git e creato da <font name='Codice'>.env.example</font>, che non contiene credenziali.")
tabella(["Variabile", "Obbligatoria", "Default", "Note"], [
    ["LMSTUDIO_BASE_URL", "sì", "—", "http/https con host, es. http://localhost:1234/v1; nel container è sostituita da host.docker.internal"],
    ["LMSTUDIO_MODEL", "sì", "—", "Identificativo restituito da GET /v1/models"],
    ["FUSO_ORARIO_PREDEFINITO", "no", "Europe/Rome", "Validato all'avvio come nome IANA"],
    ["MAX_PASSAGGI", "no", "6", "Intero ≥ 1"],
    ["LIVELLO_LOG", "no", "WARNING", "DEBUG, INFO, WARNING o ERROR; log su stderr"],
], [4.4, 2, 2.4, 7.6])
codice("""
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m assistente                      # chat locale
$env:LIVELLO_LOG="INFO"; python -m assistente   # con i log delle chiamate
""")

# 13
h1("13. Test e verifiche")
p("La strategia distingue due livelli, come chiede il CLAUDE.md: <b>test automatici</b> ripetibili che non richiedono "
  "un modello attivo, e <b>prove reali</b> con LM Studio e Docker, tenute separate e attivate esplicitamente con i "
  "marcatori pytest. <font name='Codice'>pytest.ini</font> esclude le prove reali di default "
  "(<font name='Codice'>-m \"not lmstudio and not docker\"</font>).")
tabella(["File di test", "N.", "Che cosa verifica"], [
    ["test_strumenti.py", "18", "Orologio con istante fisso: Roma inverno/estate, Tokyo, UTC, default, spazi, fusi non validi, giorno nel fuso giusto, schema inviato al modello."],
    ["test_grafo.py", "15", "Percorsi con modelli finti: solo llm; llm → strumenti → llm; limite (3 llm, 2 strumenti); strumento sconosciuto, argomenti errati o non JSON; log; instrada sui quattro casi; prompt."],
    ["test_configurazione.py", "14", "Default, variabili obbligatorie mancanti, valori non validi (MAX_PASSAGGI, LIVELLO_LOG, fuso, URL)."],
    ["test_terminale.py", "11", "esci, righe vuote, fine input e Ctrl+C, errore del modello, risposta vuota, limite, formato della riga [strumento], BOM dell'input da pipe."],
    ["test_conversazione.py", "6", "Due turni senza duplicati; rollback dopo errore di connessione e HTTP; chiamate del turno; rollback al limite."],
    ["test_modello.py", "3", "Verifica del modello: presente, assente con elenco, server irraggiungibile con avviso."],
    ["test_avvio.py", "3", "Configurazione mancante senza traceback; Ctrl+C all'avvio; output non codificabile."],
    ["reali/test_lmstudio.py", "3", "Modello reale: due turni con cronologia («Ada»); ora a Tokyo con chiamata reale e ora nella risposta; domanda ordinaria senza strumento."],
    ["reali/test_docker.py", "1", "Dal container: riga [strumento] con Asia/Tokyo e un'ora valida, e risposta che usa quell'ora."],
], [4.2, 0.9, 11.3])
h2("Modelli finti e istante controllato")
punti(
    "<b>GenericFakeChatModel</b> di LangChain e un <b>RunnableLambda «a copione»</b> (<font name='Codice'>tests/finti.py</font>) "
    "restituiscono risposte prestabilite: AIMessage di testo, richieste di tool, oppure eccezioni come un errore di connessione. "
    "Così si verificano tutti i percorsi del grafo senza dipendere da LM Studio.",
    "Lo strumento riceve un <b>orologio iniettabile</b>: <font name='Codice'>orologio=lambda: ISTANTE_INVERNO</font>.",
    "Il terminale riceve funzioni <font name='Codice'>leggi</font> e <font name='Codice'>scrivi</font> iniettabili: i test simulano input ed esaminano le righe stampate.",
)
h2("TDD: test che fallisce, modifica, test superato")
p("Ogni funzionalità è nata da un test scritto prima del codice e visto fallire (RED), poi fatto passare (GREEN). "
  "Anche i difetti trovati nelle prove reali o nella revisione sono stati corretti così: prima un test che riproduce "
  "il difetto, poi la correzione.")
riquadro("Perché servono anche le prove reali",
         "Una risposta simulata non dimostra che il modello locale sappia usare lo strumento. I test automatici provano "
         "che il <i>programma</i> gestisce correttamente richieste e risposte; solo la prova con il modello reale prova "
         "che <i>gemma-4-e2b</i> chiede davvero lo strumento con gli argomenti giusti.", sfondo=GIALLO_CHIARO, bordo=ACCENTO)
codice("""
python -m pytest                    # 70 passed, 4 deselected
python -m pytest -m lmstudio -v     # 3 passed (richiede .env e LM Studio attivo)
docker compose build
python -m pytest -m docker -v       # 1 passed (richiede Docker e LM Studio)
""")

# 14
h1("14. Metodo di lavoro: CLAUDE.md, Superpowers e Git")
h2("CLAUDE.md")
p("File di istruzioni stabili per Claude Code nella cartella del progetto: obiettivo e confini (solo questa cartella, "
  "niente MCP/RAG/web anticipati), scelte tecniche (LangGraph, LM Studio sull'host, Docker Compose, configurazione da "
  "ambiente, dipendenze fissate), metodo (Superpowers, niente codice prima di specifica e piano approvati), test, Git "
  "(Conventional Commits in italiano, staging selettivo, push solo su richiesta) e documentazione (README con soli comandi verificati).")
h2("Il ciclo di Superpowers applicato al progetto")
tabella(["Fase", "Che cosa è stato prodotto"], [
    ["Brainstorming", "Decisioni chiarite con lo studente: fuso selezionabile, chiamate visibili in chat e nei log, log silenziosi di default, cronologia persa alla chiusura."],
    ["Specifica", "docs/superpowers/specs: comportamento, contratto dello strumento, errori, test, corrispondenza con la consegna; requisiti con ID (RF, RE, RV)."],
    ["Piano", "Cinque incrementi con file, interfacce, test da scrivere prima e verifiche attese: grafo fisso, LM Studio e cronologia, orologio e instradamento, Docker, verifica completa."],
    ["Implementazione", "Esecuzione del piano in linea con TDD, un commit per incremento verificato, registro delle decisioni."],
    ["Review e verifica", "Revisione indipendente di tutto il lavoro: nessun problema critico; corretti 5 problemi importanti, ognuno partendo da un test che falliva."],
    ["Integrazione", "README e CLAUDE.md aggiornati, guida all'avvio, handoff per riprendere il lavoro, push su richiesta dello studente."],
], [3.2, 13.2])
h2("Commit (Conventional Commits)")
tabella(["Commit", "Messaggio"], [
    ["fc76c65", "docs(spec): aggiungi specifica e requisiti e sposta CLAUDE.md nel progetto"],
    ["ac06cbd", "feat(grafo): aggiungi la struttura del progetto e il grafo con risposta fissa"],
    ["ece47a7", "docs(piano): aggiungi il piano di implementazione approvato"],
    ["d8f214c", "feat(modello): collega LM Studio e conserva la cronologia della sessione"],
    ["da96444", "feat(terminale): aggiungi la chat da terminale e l'avvio"],
    ["fe86f84", "feat(strumenti): aggiungi lo strumento orologio con fuso orario esplicito"],
    ["4342b15", "docs: aggiungi l'handoff della sessione"],
    ["500c58f", "feat(grafo): instrada le richieste di tool verso lo strumento orologio con limite di passaggi"],
    ["3f1db2c", "feat(docker): avvia l'assistente con Docker Compose e LM Studio sull'host"],
    ["5dc02b7", "fix(grafo): restituisci un errore al modello per le richieste di tool con argomenti non validi"],
    ["63d08d9", "fix(avvio): evita traceback con URL non valido, Ctrl+C all'avvio e output rediretto"],
    ["865945d", "test(docker): verifica che la risposta dal container usi l'ora restituita dallo strumento"],
    ["fe0085e", "feat(strumenti): aggiungi il giorno della settimana al risultato dell'orologio"],
    ["bbe18d9", "docs: completa README e CLAUDE.md dopo la verifica finale"],
    ["a188fc8", "docs(esposizione): aggiungi la guida PDF per l'esposizione e lo script che la genera"],
    ["edd9583", "fix(terminale): ignora il BOM che PowerShell antepone all'input passato con una pipe"],
    ["f47ef87", "docs: aggiungi la guida passo per passo per avviare l'assistente"],
    ["30c21a4", "docs(esposizione): aggiungi il promemoria di 5 pagine e lo script che lo genera"],
    ["6894673", "docs: togli dal README la nota sulla chat Docker interattiva, ora verificata"],
    ["b5b0db4", "style(terminale): scrivi il BOM come sequenza \\ufeff invece del carattere invisibile"],
], [2.2, 14.2])

# 15
h1("15. Risultati, misure e decisioni")
h2("Affidabilità del tool calling con il modello reale")
tabella(["Versione", "Ora a Tokyo con fuso_orario=Asia/Tokyo", "Domanda ordinaria senza strumento"], [
    ["Descrizione dello strumento senza descrizione del parametro", "12 su 17 (in 5 casi chiamata senza fuso: ora di Roma)", "9 su 9"],
    ["Con descrizione del parametro e frase nel prompt di sistema", "12 su 12", "12 su 12"],
], [6.2, 6.2, 4])
p("Il modello ha sempre chiamato lo strumento (mai un'ora inventata); il problema era l'argomento mancante. Il test "
  "reale non è stato ammorbidito: si è migliorato il contratto. Il modello resta non deterministico, quindi un errore "
  "occasionale va segnalato, non nascosto.")
h2("Giorno della settimana")
p("In una prova il modello ha scritto «lunedì 28 ottobre» (era mercoledì): il giorno non era nel risultato e il modello "
  "lo calcolava da sé. Su decisione dello studente il giorno è stato aggiunto al risultato e la specifica aggiornata. "
  "Nelle prove successive il modello ha usato il giorno corretto restituito dallo strumento.")
h2("Dove va il tempo di risposta")
tabella(["Richiesta", "Totale", "Primo token", "Generazione", "Token generati"], [
    ["Ora a Tokyo, 1a chiamata (richiesta dello strumento)", "6,8 s", "0,6 s", "4,4 s", "63"],
    ["Ora a Tokyo, 2a chiamata (risposta)", "8,6–9,2 s", "0,8 s", "6,3–6,9 s", "90–99"],
    ["Capitale della Francia", "12,5–14 s", "0,3–0,8 s", "10–11,6 s", "157–179"],
    ["Ora a Tokyo dopo 10 turni di cronologia", "13,8 s", "7,3 s", "11,3 s", "62"],
], [6.6, 2.2, 2.2, 2.6, 2.8])
punti(
    "<b>Causa principale: ragionamento nascosto</b>. Per la capitale della Francia, 176 token su 188 sono "
    "<i>reasoning_tokens</i>; la risposta visibile ne usa circa 8.",
    "<b>Generazione a circa 16 token/s</b> e lettura del prompt lenta con cronologie lunghe: probabile esecuzione in buona "
    "parte su CPU (da verificare il GPU Offload in LM Studio).",
    "Lo strumento impiega millisecondi; Docker non aggiunge tempi apprezzabili.",
    "Con il parametro <font name='Codice'>reasoning_effort=\"none\"</font> la stessa domanda è scesa da 11,9 s a 3,6 s "
    "(0 token di ragionamento). Non è stato adottato: l'affidabilità 12 su 12 è stata misurata con il ragionamento attivo "
    "e andrebbe rimisurata prima di cambiare.",
)
h2("Revisione indipendente")
p("Esito: «pronto con correzioni», nessun problema critico, i cinque punti del focus di revisione soddisfatti. "
  "Corretti: richieste con argomenti non JSON ignorate; prova Docker che passava anche con un errore dello strumento; "
  "traceback con URL malformato, con Ctrl+C all'avvio e con output rediretto.")

# 16
h1("16. Limiti, problemi aperti e prossimi passi")
tabella(["Punto aperto", "Stato"], [
    ["LM Studio spento davvero", "Simulato con una porta chiusa; comportamento coperto anche dai test."],
    ["Ctrl+C in una chat interattiva", "Coperto dai test automatici, non provato dal vivo."],
    ["La prova Docker non ricostruisce l'immagine", "Eseguire prima docker compose build (scritto in CLAUDE.md)."],
    ["Risposta del modello fatta di soli spazi", "Stampa Assistente&gt; vuoto invece del testo previsto (minore)."],
    ["Tempi di risposta", "Dominati dal ragionamento nascosto del modello; possibile ottimizzazione da decidere."],
], [7.2, 9.2])
h2("Prossime lezioni")
p("Il progetto è la base delle lezioni successive: altri strumenti, MCP, workflow e RAG estenderanno questo codice e "
  "questo grafo. I punti di estensione sono già presenti: la lista <font name='Codice'>strumenti</font> (un nuovo "
  "strumento è un altro BaseTool), il nodo strumenti generico che cerca per nome, lo stato del grafo a cui aggiungere "
  "campi, la configurazione centralizzata.")

# 17
h1("17. Come impostare l'esposizione")
h2("Scaletta suggerita (circa 12 minuti)")
tabella(["Tempo", "Parte", "Messaggio chiave"], [
    ["1 min", "Obiettivo", "Chatbot locale con grafo esplicito, strumento orologio reale, Docker. Requisiti della slide 26."],
    ["2 min", "Teoria LangGraph", "Stato, nodi, archi, reducer add_messages; dal grafo con risposta fissa al ciclo con strumenti (Figura 1)."],
    ["2 min", "Teoria tool calling", "Il modello chiede, il programma esegue; la descrizione è il contratto; tool_call_id."],
    ["1 min", "Architettura", "Moduli piccoli e separati (Figura 3); LM Studio sull'host (Figura 2)."],
    ["3 min", "Demo", "Domanda ordinaria, domanda sull'ora con riga [strumento], log INFO, avvio in Docker."],
    ["2 min", "Test e metodo", "70 test senza modello, prove reali separate, TDD, Superpowers, Conventional Commits."],
    ["1 min", "Risultati e limiti", "12/17 → 12/12, giorno della settimana, tempi e ragionamento nascosto, punti aperti."],
], [1.6, 3.2, 11.6])
h2("Script della demo")
codice("""
# 1. Locale, con i log delle chiamate
.\\.venv\\Scripts\\Activate.ps1
$env:LIVELLO_LOG="INFO"
python -m assistente
Tu> Qual è la capitale della Francia?     (nessuna riga [strumento])
Tu> Che ore sono adesso a Tokyo?          (riga [strumento] + log di instradamento)
Tu> E a Roma?                             (la cronologia fa capire il riferimento)
Tu> esci

# 2. Docker (LM Studio resta sull'host)
docker compose build
docker compose run --rm --name assistente-demo -e LIVELLO_LOG=INFO assistente
#    da un secondo terminale:
docker ps
docker logs -f assistente-demo

# 3. Test
python -m pytest
""")
riquadro("Consigli pratici",
         "Avviare LM Studio e caricare il modello prima della demo (la prima chiamata è più lenta). Avvisare che ogni "
         "risposta richiede alcuni secondi e spiegare perché (ragionamento nascosto, due chiamate per le domande "
         "sull'ora). Tenere pronta una traccia di log già ottenuta, nel caso il modello rallenti.")

# 18
h1("18. Domande probabili e risposte")
qa = [
    ("Perché usare LangGraph e non un semplice ciclo while?",
     "Perché il flusso diventa esplicito e verificabile: stato, nodi e instradamento sono riconoscibili, i test possono "
     "controllare quali nodi sono stati eseguiti, e aggiungere strumenti o passaggi nelle prossime lezioni non richiede "
     "di riscrivere il ciclo."),
    ("Il modello esegue la funzione dell'orologio?",
     "No. Il modello produce solo una richiesta strutturata (nome e argomenti JSON). La funzione Python viene eseguita dal "
     "nodo strumenti e il risultato torna al modello come ToolMessage."),
    ("Come fate a sapere che l'ora non è inventata?",
     "Dalla traccia: riga [strumento] in chat e log INFO con richiesta, esecuzione e risultato; il test reale controlla "
     "che la risposta contenga l'ora HH:MM restituita dallo strumento."),
    ("Dove viene conservata la memoria della conversazione?",
     "Nell'applicazione, non nel modello: la classe Conversazione tiene la lista dei messaggi e la reinvia a ogni turno. "
     "Il reducer add_messages aggiunge le nuove risposte senza sostituire la cronologia. Alla chiusura viene persa."),
    ("Che cosa succede se LM Studio è spento?",
     "All'avvio compare un avviso; durante la chat un errore con l'indirizzo provato e un suggerimento. La sessione resta "
     "aperta e la cronologia torna com'era prima della domanda. Nessuna risposta inventata."),
    ("A che cosa serve il limite di passaggi?",
     "A interrompere cicli che non terminano, per esempio un modello che chiede lo strumento all'infinito. Al limite il "
     "turno finisce con un messaggio esplicito e il rollback."),
    ("Perché il fuso orario è un parametro e non fisso?",
     "Per rispondere su qualsiasi luogo («che ore sono a Tokyo?»). Il parametro è validato come nome IANA e un valore non "
     "valido produce un errore testuale per il modello, non un'eccezione."),
    ("Perché l'ora non dipende dal fuso del container?",
     "Perché l'istante si legge in UTC e si converte nel fuso richiesto con zoneinfo e tzdata. Nel container (in UTC) lo "
     "strumento restituiva correttamente l'ora di Tokyo."),
    ("Come comunica il container con LM Studio?",
     "Con una connessione in uscita verso http://host.docker.internal:1234/v1, il nome con cui Docker Desktop raggiunge "
     "l'host. Non serve pubblicare porte; localhost nel container indicherebbe il container stesso."),
    ("Come si testa un grafo senza modello?",
     "Con modelli finti che restituiscono risposte prestabilite (testo, richieste di tool, eccezioni) e con un istante "
     "fisso per l'orologio. I test verificano percorsi, ToolMessage, limite, rollback e log."),
    ("Perché le risposte sono lente?",
     "Il modello genera prima un ragionamento nascosto di circa 140–195 token a circa 16 token/s; le domande sull'ora "
     "richiedono due chiamate. Con reasoning_effort=\"none\" una risposta è scesa da 11,9 a 3,6 s, ma va rimisurata "
     "l'affidabilità del tool calling prima di adottarlo."),
    ("Che cosa avete cambiato dopo le prove reali?",
     "La descrizione del parametro fuso_orario e il prompt (12/17 → 12/12) e il giorno della settimana nel risultato. "
     "I test non sono stati ammorbiditi: è stato migliorato il contratto."),
    ("Come si aggiunge un nuovo strumento?",
     "Si crea un altro BaseTool e lo si aggiunge alla lista strumenti passata a crea_modello e crea_grafo: il nodo "
     "strumenti lo trova per nome senza altre modifiche al grafo."),
]
for domanda, risposta in qa:
    storia.append(KeepTogether([Paragraph(domanda, S["domanda"]), Paragraph(risposta, S["corpo"])]))

# 19
h1("19. Glossario")
tabella(["Termine", "Definizione"], [
    ["Agente", "Programma in cui un LLM può decidere di usare strumenti in un ciclo, fino a una risposta finale."],
    ["Arco condizionale", "Collegamento del grafo il cui nodo di destinazione è scelto da una funzione sullo stato."],
    ["Checkpointer", "Componente LangGraph che salva lo stato tra invocazioni (non usato nel progetto)."],
    ["Contesto", "Numero massimo di token che il modello considera in una chiamata (qui 8192)."],
    ["Conventional Commits", "Convenzione dei messaggi di commit: tipo(ambito): descrizione, es. feat(grafo): …"],
    ["GGUF", "Formato di file per modelli quantizzati eseguiti da llama.cpp e LM Studio."],
    ["IANA (fuso)", "Database standard dei fusi orari, con nomi come Europe/Rome e regole dell'ora legale."],
    ["ISO 8601", "Standard di rappresentazione di data e ora, es. 2026-10-28T20:08:51+09:00."],
    ["JSON Schema", "Formato con cui si descrivono i parametri di uno strumento al modello."],
    ["Quantizzazione", "Riduzione della precisione dei pesi (es. a 4 bit) per ridurre memoria e calcolo."],
    ["Reducer", "Funzione che combina l'aggiornamento di un nodo con lo stato esistente (add_messages)."],
    ["Rollback", "Ripristino della cronologia com'era prima di un turno fallito."],
    ["Runnable", "Interfaccia LangChain con invoke/stream, comune a modelli, strumenti e grafi compilati."],
    ["TDD", "Test-Driven Development: test che fallisce, codice minimo che lo fa passare, poi pulizia."],
    ["Token", "Frammento di testo su cui il modello lavora; si misura la velocità in token al secondo."],
    ["Tool calling", "Meccanismo con cui il modello richiede in forma strutturata l'uso di una funzione del programma."],
    ["tool_call_id", "Identificativo che associa il risultato di uno strumento alla richiesta del modello."],
    ["TTY", "Terminale interattivo; in Docker si attiva con -it o stdin_open + tty."],
], [3.8, 12.6])

doc = SimpleDocTemplate(USCITA, pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm, topMargin=2 * cm,
                        bottomMargin=2.2 * cm, title="Assistente del laboratorio — guida per l'esposizione",
                        author="Brandon", subject="Lezione 4 · Dal client a un agente LangGraph")
doc.build(storia, onFirstPage=copertina, onLaterPages=piede)
print("scritto", USCITA)
