from assistente.__main__ import main


def test_configurazione_mancante_termina_con_messaggio(capsys):
    assert main({}) == 1
    errori = capsys.readouterr().err
    assert "LMSTUDIO_BASE_URL" in errori
    assert "Traceback" not in errori
