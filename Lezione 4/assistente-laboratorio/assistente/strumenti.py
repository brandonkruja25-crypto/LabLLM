"""Strumenti a disposizione del modello: per ora solo l'orologio con fuso orario esplicito."""

from collections.abc import Callable
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.tools import BaseTool, StructuredTool

ESEMPI_FUSO = "Europe/Rome, Asia/Tokyo, America/New_York, UTC"


def valida_fuso(nome: str) -> ZoneInfo:
    """ZoneInfo per un nome IANA; ValueError se vuoto, sconosciuto o non valido."""
    nome = nome.strip()
    if not nome:
        raise ValueError("fuso orario vuoto")
    try:
        return ZoneInfo(nome)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        raise ValueError(f"fuso orario sconosciuto: {nome!r}") from None


def ora_corrente_testo(fuso_orario: str | None, fuso_predefinito: str, adesso_utc: datetime) -> str:
    """Data e ora di adesso_utc nel fuso richiesto, oppure un testo che inizia con «Errore:»."""
    richiesto = fuso_predefinito if fuso_orario is None else fuso_orario
    try:
        zona = valida_fuso(richiesto)
    except ValueError:
        return (
            f"Errore: fuso orario non riconosciuto: {richiesto!r}. "
            f"Usa un nome di fuso IANA, per esempio Asia/Tokyo ({ESEMPI_FUSO})."
        )
    return f"{adesso_utc.astimezone(zona).isoformat(timespec='seconds')} ({zona.key})"


def _adesso_utc() -> datetime:
    return datetime.now(timezone.utc)


def crea_strumento_orologio(fuso_predefinito: str, orologio: Callable[[], datetime] = _adesso_utc) -> BaseTool:
    def ora_corrente(fuso_orario: str | None = None) -> str:
        return ora_corrente_testo(fuso_orario, fuso_predefinito, orologio())

    return StructuredTool.from_function(
        ora_corrente,
        name="ora_corrente",
        description=(
            "Restituisce la data e l'ora attuali. Usala ogni volta che servono la data o l'ora "
            "correnti, senza inventarle. Il parametro fuso_orario è un nome di fuso IANA, per "
            f"esempio {ESEMPI_FUSO}. Se lo ometti viene usato il fuso predefinito ({fuso_predefinito})."
        ),
    )
