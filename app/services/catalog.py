"""Catálogo de ejemplo en memoria (en el producto real vive en PostgreSQL, por negocio)."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class PriceTier:
    min_guests: int
    max_guests: int | None  # None = sin límite
    price: Decimal


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int
    tiers: list[PriceTier] = field(default_factory=list)


EVENT_TYPES = ["Boda", "Comunión", "Cumpleaños", "Evento de empresa"]

ROOMS = [
    Room(
        id="jardin",
        name="Salón Jardín",
        capacity=150,
        tiers=[
            PriceTier(1, 50, Decimal("1200")),
            PriceTier(51, 100, Decimal("1800")),
            PriceTier(101, None, Decimal("2500")),
        ],
    ),
    Room(
        id="cristal",
        name="Sala Cristal",
        capacity=60,
        tiers=[
            PriceTier(1, 30, Decimal("600")),
            PriceTier(31, None, Decimal("900")),
        ],
    ),
]


def rooms_for(guests: int) -> list[Room]:
    """Salas con aforo suficiente. (La disponibilidad real por fecha no se incluye en la muestra.)"""
    return [r for r in ROOMS if r.capacity >= guests]


def find_room(room_id: str) -> Room | None:
    return next((r for r in ROOMS if r.id == room_id), None)
