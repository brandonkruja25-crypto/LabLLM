"""Strumenti a disposizione del modello: per ora solo l'orologio con fuso orario esplicito."""

from collections.abc import Callable
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.tools import BaseTool, StructuredTool

ESEMPI_FUSO = "Europe/Rome, Asia/Tokyo, America/New_York, UTC"
# Nomi italiani fissi: strftime("%A") dipenderebbe dal locale del sistema o del container.
GIORNI = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")


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
    locale = adesso_utc.astimezone(zona)
    return f"{locale.isoformat(timespec='seconds')} ({zona.key}), {GIORNI[locale.weekday()]}"


def _adesso_utc() -> datetime:
    return datetime.now(timezone.utc)


def crea_strumento_orologio(fuso_predefinito: str, orologio: Callable[[], datetime] = _adesso_utc) -> BaseTool:
    def ora_corrente(fuso_orario: str | None = None) -> str:
        """Data, ora e giorno della settimana attuali.

        Args:
            fuso_orario: nome di fuso IANA del luogo di cui si chiede l'ora, per esempio
                Asia/Tokyo per Tokyo o America/New_York per New York. Indicalo sempre quando la
                domanda nomina una città o un paese; omettilo solo per l'ora locale.
        """
        return ora_corrente_testo(fuso_orario, fuso_predefinito, orologio())

    return StructuredTool.from_function(
        ora_corrente,
        name="ora_corrente",
        parse_docstring=True,
        description=(
            "Restituisce la data, l'ora e il giorno della settimana attuali. Usala ogni volta che "
            "servono data, ora o giorno correnti, senza inventarli. Il parametro fuso_orario è un "
            "nome di fuso IANA, per "
            f"esempio {ESEMPI_FUSO}. Se lo ometti viene usato il fuso predefinito ({fuso_predefinito})."
        ),
    )
