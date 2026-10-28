from assistente.__main__ import main


def test_configurazione_mancante_termina_con_messaggio(capsys):
    assert main({}) == 1
    errori = capsys.readouterr().err
    assert "LMSTUDIO_BASE_URL" in errori
    assert "Traceback" not in errori


def test_ctrl_c_durante_l_avvio_esce_senza_traceback(monkeypatch, capsys):
    import assistente.__main__ as avvio

    def interrompi(*argomenti, **opzioni):
        raise KeyboardInterrupt

    monkeypatch.setattr(avvio, "verifica_modello", interrompi)
    ambiente = {"LMSTUDIO_BASE_URL": "http://localhost:1234/v1", "LMSTUDIO_MODEL": "google/gemma-4-e2b"}
    assert main(ambiente) == 130


def test_output_rediretto_non_codificabile_non_solleva(monkeypatch):
    import io
    import sys

    import assistente.__main__ as avvio

    flusso = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    monkeypatch.setattr(sys, "stdout", flusso)
    monkeypatch.setattr(avvio, "verifica_modello", lambda *a, **k: None)
    monkeypatch.setattr(avvio, "esegui_chat", lambda conversazione: print("[strumento] ora_corrente() → R"))
    ambiente = {"LMSTUDIO_BASE_URL": "http://localhost:1234/v1", "LMSTUDIO_MODEL": "google/gemma-4-e2b"}
    assert main(ambiente) == 0
    flusso.flush()
    assert "ora_corrente() " in flusso.buffer.getvalue().decode("cp1252")
