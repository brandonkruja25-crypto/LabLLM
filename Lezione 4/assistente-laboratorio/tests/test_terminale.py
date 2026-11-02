import pytest

from assistente.conversazione import ChiamataStrumento, ErroreModello, EsitoTurno
from assistente.terminale import esegui_chat, formatta_chiamata


class ConversazioneFinta:
    """Restituisce (o solleva) gli esiti prestabiliti, uno per ogni invio."""

    def __init__(self, *esiti):
        self.esiti = list(esiti)
        self.inviati = []

    def invia(self, testo):
        self.inviati.append(testo)
        esito = self.esiti.pop(0)
        if isinstance(esito, BaseException):
            raise esito
        return esito


def chat(conversazione, ingressi):
    """Esegue la chat con input prestabiliti; restituisce le righe scritte."""
    coda = list(ingressi)
    righe = []

    def leggi(prompt):
        passo = coda.pop(0)
        if isinstance(passo, BaseException):
            raise passo
        return passo

    esegui_chat(conversazione, leggi=leggi, scrivi=righe.append)
    return righe


def test_turno_normale_ed_esci():
    conv = ConversazioneFinta(EsitoTurno("Ciao!"))
    righe = chat(conv, ["ciao", "esci"])
    assert "Assistente> Ciao!" in righe
    assert conv.inviati == ["ciao"]


def test_righe_vuote_ignorate():
    conv = ConversazioneFinta()
    chat(conv, ["", "   ", "esci"])
    assert conv.inviati == []


@pytest.mark.parametrize("interruzione", [EOFError(), KeyboardInterrupt()], ids=["fine-input", "ctrl-c"])
def test_fine_input_e_ctrl_c(interruzione):
    chat(ConversazioneFinta(), [interruzione])


def test_ctrl_c_durante_la_risposta():
    conv = ConversazioneFinta(KeyboardInterrupt())
    chat(conv, ["ciao"])
    assert conv.inviati == ["ciao"]


def test_errore_modello_mostrato_e_sessione_aperta():
    conv = ConversazioneFinta(ErroreModello("x"), EsitoTurno("Eccomi."))
    righe = chat(conv, ["ciao", "ci sei?", "esci"])
    assert righe.index("Errore: x") < righe.index("Assistente> Eccomi.")


def test_risposta_vuota():
    righe = chat(ConversazioneFinta(EsitoTurno("")), ["ciao", "esci"])
    assert "Assistente> (il modello non ha restituito testo)" in righe


def test_limite_raggiunto():
    righe = chat(ConversazioneFinta(EsitoTurno(None, [], True)), ["ciao", "esci"])
    assert "Limite di passaggi raggiunto: nessuna risposta finale. Riformula la domanda." in righe
    assert not any(r.startswith("Assistente>") for r in righe)


def test_formatta_chiamata():
    assert (
        formatta_chiamata(ChiamataStrumento("ora_corrente", {"fuso_orario": "Asia/Tokyo"}, "R"))
        == '[strumento] ora_corrente(fuso_orario="Asia/Tokyo") → R'
    )
    assert formatta_chiamata(ChiamataStrumento("ora_corrente", {}, "R")) == "[strumento] ora_corrente() → R"


def test_chiamate_stampate_prima_della_risposta():
    chiamata = ChiamataStrumento("ora_corrente", {"fuso_orario": "Asia/Tokyo"}, "R")
    righe = chat(ConversazioneFinta(EsitoTurno("Sono le 21.", [chiamata])), ["ore?", "esci"])
    assert righe.index(formatta_chiamata(chiamata)) < righe.index("Assistente> Sono le 21.")


def test_bom_iniziale_ignorato():
    """PowerShell, passando l'input con una pipe, antepone il BOM (U+FEFF) al primo testo."""
    conv = ConversazioneFinta(EsitoTurno("Ciao!"))
    chat(conv, ["﻿ciao", "esci"])
    assert conv.inviati == ["ciao"]

    conv = ConversazioneFinta()
    chat(conv, ["﻿esci"])
    assert conv.inviati == []
