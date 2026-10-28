"""Prova reale con Docker Compose: python -m pytest -m docker -v (richiede Docker, .env e LM Studio)."""

import re
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.docker

RADICE = Path(__file__).resolve().parents[2]


def test_orologio_dal_container():
    esito = subprocess.run(
        ["docker", "compose", "run", "--rm", "-T", "assistente"],
        input="Che ore sono adesso a Tokyo?\nesci\n",
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=300,
        cwd=RADICE,
    )
    traccia = f"stdout: {esito.stdout!r}\nstderr: {esito.stderr!r}"
    assert esito.returncode == 0, traccia
    verifica_traccia_orologio(esito.stdout, traccia)


def verifica_traccia_orologio(stdout: str, traccia: str = "") -> None:
    """Riga [strumento] con Asia/Tokyo e un'ora valida, e risposta che usa quell'ora."""
    chiamata = re.search(
        r'\[strumento\] ora_corrente\(fuso_orario="Asia/Tokyo"\) → \d{4}-\d\d-\d\dT(\d\d:\d\d)', stdout
    )
    assert chiamata, traccia or stdout
    risposte = [riga for riga in stdout.splitlines() if "Assistente>" in riga]
    assert any(chiamata.group(1) in riga for riga in risposte), traccia or stdout
