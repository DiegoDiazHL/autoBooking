"""Chatea con el bot de la demo en la terminal. Escribe «salir» para terminar."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.flows.customer_flow import Conversation, handle  # noqa: E402


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    conv = Conversation()
    print("Demo del bot de reservas (escribe «salir» para terminar)\n")
    while True:
        try:
            text = input("Tú  ▸ ")
        except (EOFError, KeyboardInterrupt):
            break
        print("Bot ▸ " + handle(conv, text).replace("\n", "\n      ") + "\n")
        if text.strip().lower() == "salir":
            break


if __name__ == "__main__":
    main()
