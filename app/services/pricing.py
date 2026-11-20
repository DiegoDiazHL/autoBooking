"""Precio de una sala por tramos de invitados (versión simplificada para la muestra)."""

from decimal import Decimal

from app.services.catalog import Room


def room_price(room: Room, guests: int) -> Decimal | None:
    """Precio cerrado del tramo que cubre a esos invitados, o None si ninguno lo cubre."""
    for tier in room.tiers:
        if guests >= tier.min_guests and (tier.max_guests is None or guests <= tier.max_guests):
            return tier.price
    return None


def format_eur(amount: Decimal) -> str:
    return f"{amount:,.0f} €".replace(",", ".")
