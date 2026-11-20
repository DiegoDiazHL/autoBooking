"""API de la demo. En el producto real aquí entran el webhook de WhatsApp y la API del panel."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.flows.customer_flow import Conversation, handle

app = FastAPI(
    title="AutoBooking — Showcase",
    description="Demo reducida de un producto real de reservas de salones por WhatsApp.",
)

# Conversaciones en memoria, por teléfono (solo para la demo).
_conversations: dict[str, Conversation] = {}


class ChatIn(BaseModel):
    phone: str
    text: str


class ChatOut(BaseModel):
    reply: str
    state: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/demo/chat", response_model=ChatOut)
def demo_chat(msg: ChatIn) -> ChatOut:
    conv = _conversations.setdefault(msg.phone, Conversation())
    reply = handle(conv, msg.text)
    return ChatOut(reply=reply, state=conv.state)
