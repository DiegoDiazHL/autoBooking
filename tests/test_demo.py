from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.flows.customer_flow import Conversation, handle
from app.main import app
from app.services import catalog, pricing

TODAY = date(2026, 1, 10)


def test_precio_por_tramo():
    jardin = catalog.find_room("jardin")
    assert pricing.room_price(jardin, 50) == Decimal("1200")
    assert pricing.room_price(jardin, 51) == Decimal("1800")
    assert pricing.room_price(jardin, 140) == Decimal("2500")


def test_conversacion_completa():
    conv = Conversation()
    assert "evento" in handle(conv, "Hola", TODAY)
    assert "fecha" in handle(conv, "Un cumpleaños", TODAY)
    assert "invitados" in handle(conv, "el 12 de abril", TODAY)
    assert "Sala Cristal" in handle(conv, "entre 40 y 50", TODAY)
    assert "900 €" in handle(conv, "2", TODAY)
    resumen = handle(conv, "laura", TODAY)
    assert "12/04/2026" in resumen and "50 invitados" in resumen and "Laura" in resumen
    assert "confirmada" in handle(conv, "sí", TODAY)
    assert conv.state == "IDLE"


def test_primer_mensaje_con_datos_solo_pregunta_lo_que_falta():
    conv = Conversation()
    reply = handle(conv, "Queremos una comunión el 14 de junio, seremos unos 80", TODAY)
    assert conv.state == "SELECTING_ROOM"
    assert "Salón Jardín" in reply and "Sala Cristal" not in reply


def test_cancelar_borra_el_borrador():
    conv = Conversation()
    handle(conv, "Una boda el 3 de mayo", TODAY)
    handle(conv, "cancelar", TODAY)
    assert conv.state == "IDLE" and conv.draft.event_type is None


def test_api_demo():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    r = client.post("/demo/chat", json={"phone": "600000000", "text": "Hola"})
    assert r.status_code == 200 and r.json()["state"] == "COLLECTING"
