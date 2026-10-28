"""Prova reale con Docker Compose: python -m pytest -m docker -v (richiede Docker, .env e LM Studio)."""

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
    assert "[strumento] ora_corrente(" in esito.stdout, traccia
    assert "Asia/Tokyo" in esito.stdout, traccia
