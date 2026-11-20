"""Máquina de estados del cliente — versión reducida para la demo.

El producto real añade extracción con IA, validación de fechas y bloqueos, disponibilidad real,
fotos, extras, cupones, encuesta, avisos al equipo, persistencia, etc. Aquí solo se muestra la
forma general: un borrador que se va rellenando y un paso siguiente que depende de lo que falta.
"""

import re
from dataclasses import dataclass, field
from datetime import date

from app.services import catalog, pricing

MONTHS = {
    m: i
    for i, m in enumerate(
        ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"],
        start=1,
    )
}
CANCEL_WORDS = {"cancelar", "salir", "adios", "adiós"}
YES_WORDS = {"si", "sí", "vale", "ok", "confirmo"}


@dataclass
class Draft:
    event_type: str | None = None
    event_date: date | None = None
    guests: int | None = None
    room_id: str | None = None
    name: str | None = None


@dataclass
class Conversation:
    state: str = "IDLE"
    draft: Draft = field(default_factory=Draft)


# ── extracción muy básica (en el real: reglas completas + IA) ──────────────────────────────

def _parse_event_type(text: str) -> str | None:
    low = text.lower()
    return next((t for t in catalog.EVENT_TYPES if t.lower() in low), None)


def _parse_date(text: str, today: date) -> date | None:
    m = re.search(r"\b(\d{1,2}) de (" + "|".join(MONTHS) + r")\b", text.lower())
    if not m:
        return None
    day, month = int(m.group(1)), MONTHS[m.group(2)]
    year = today.year if (month, day) > (today.month, today.day) else today.year + 1
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _parse_guests(text: str, asked: bool) -> int | None:
    """Si se acaba de preguntar, vale un número o un rango («entre 40 y 50» → el mayor).
    Si no, solo cuenta un número con contexto («80 invitados», «seremos unos 80»)."""
    low = text.lower()
    if not asked:
        m = re.search(r"\b(\d{1,4})\s*(invitados|personas)\b", low) or re.search(
            r"\b(?:somos|seremos)(?: unos| unas)? (\d{1,4})\b", low
        )
        return int(m.group(1)) if m else None
    numbers = [int(n) for n in re.findall(r"\b\d{1,4}\b", low)]
    return max(numbers) if numbers and max(numbers) > 0 else None


# ── flujo ─────────────────────────────────────────────────────────────────────────────────

def handle(conv: Conversation, text: str, today: date | None = None) -> str:
    today = today or date.today()
    text = text.strip()
    d = conv.draft

    if text.lower() in CANCEL_WORDS:
        conv.state, conv.draft = "IDLE", Draft()
        return "Sin problema, lo dejamos aquí. ¡Escríbenos cuando quieras!"

    if conv.state == "SELECTING_ROOM":
        rooms = catalog.rooms_for(d.guests or 1)
        if text.isdigit() and 1 <= int(text) <= len(rooms):
            d.room_id = rooms[int(text) - 1].id
        else:
            return "Elige una sala escribiendo su número."
    elif conv.state == "COLLECTING_NAME":
        d.name = text.title()
    elif conv.state == "CONFIRMING":
        if text.lower() in YES_WORDS:
            conv.state, conv.draft = "IDLE", Draft()
            return "✅ ¡Reserva confirmada! El salón se pondrá en contacto contigo para la fianza."
        return "Responde *sí* para confirmar o *cancelar* para dejarlo."
    else:
        # Aprovecha todo lo que traiga el mensaje: solo se pregunta lo que falta.
        d.event_type = d.event_type or _parse_event_type(text)
        d.event_date = d.event_date or _parse_date(text, today)
        if d.guests is None:
            d.guests = _parse_guests(text, asked=conv.state == "COLLECTING_GUESTS")

    return _advance(conv)


def _advance(conv: Conversation) -> str:
    d = conv.draft
    if d.event_type is None:
        conv.state = "COLLECTING"
        options = ", ".join(catalog.EVENT_TYPES)
        return f"¡Hola! ¿Qué evento queréis celebrar? ({options})"
    if d.event_date is None:
        conv.state = "COLLECTING"
        return f"¡Genial, {d.event_type.lower()}! ¿Para qué fecha? (p. ej. «12 de abril»)"
    if d.guests is None:
        conv.state = "COLLECTING_GUESTS"
        return "¿Cuántos invitados seréis aproximadamente?"
    if d.room_id is None:
        rooms = catalog.rooms_for(d.guests)
        if not rooms:
            d.guests = None
            conv.state = "COLLECTING_GUESTS"
            return "No tenemos salas para tantos invitados. ¿Cuántos seréis?"
        conv.state = "SELECTING_ROOM"
        lines = [f"{i}) {r.name} (hasta {r.capacity})" for i, r in enumerate(rooms, start=1)]
        return "Estas salas están disponibles:\n" + "\n".join(lines)
    room = catalog.find_room(d.room_id)
    price = pricing.room_price(room, d.guests)
    if d.name is None:
        conv.state = "COLLECTING_NAME"
        return f"{room.name} para {d.guests} invitados: {pricing.format_eur(price)}. ¿A nombre de quién?"
    conv.state = "CONFIRMING"
    return (
        "Resumen:\n"
        f"• {d.event_type}\n"
        f"• {d.event_date:%d/%m/%Y}\n"
        f"• {d.guests} invitados\n"
        f"• {room.name}\n"
        f"• A nombre de {d.name}\n"
        f"• Total: {pricing.format_eur(price)}\n"
        "¿Confirmamos? (sí / cancelar)"
    )
