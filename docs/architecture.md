# Arquitectura

Vista general del producto real. Esta muestra solo implementa una versión reducida del flujo del
cliente.

## Canales

```mermaid
flowchart TB
    subgraph Entrada
        W[Webhook de WhatsApp]
        P[API del panel]
    end
    W --> R{¿Quién escribe?}
    R -->|miembro del equipo| A[Flujo de equipo]
    R -->|cliente| C[Flujo de cliente]
    P --> S
    A --> S[Servicios de dominio]
    C --> S
    S --> DB[(PostgreSQL)]
```

- **Un número de WhatsApp por negocio**: el mensaje entrante identifica el negocio y, dentro de
  él, si quien escribe es del equipo o un cliente.
- **Servicios compartidos**: WhatsApp y el panel usan las mismas reglas de negocio, así no hay
  dos versiones de la verdad.

## Conversación del cliente

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> COLLECTING: saludo o primer dato
    COLLECTING --> COLLECTING: falta tipo / fecha / invitados
    COLLECTING --> SELECTING_ROOM: datos completos
    SELECTING_ROOM --> COLLECTING_NAME: sala elegida (se da su precio)
    COLLECTING_NAME --> CONFIRMING: nombre
    CONFIRMING --> [*]: confirma
    CONFIRMING --> IDLE: cancela
```

Principios de diseño:

- **Determinista antes que IA**: la IA solo ayuda a extraer datos del texto libre; las fechas,
  los números y los precios se validan con reglas.
- **Las elecciones de listas llegan como identificadores**, no como texto libre.
- **Solo se pregunta lo que falta**: si el primer mensaje ya trae datos, se aprovechan.

## Ciclo de vida de una reserva (simplificado)

```mermaid
stateDiagram-v2
    [*] --> CONFIRMADA: el cliente confirma
    CONFIRMADA --> RESERVADA: el salón registra la fianza
    CONFIRMADA --> NO_RESERVADA: vence el plazo
    RESERVADA --> CELEBRADA: pasa el evento
    CONFIRMADA --> CANCELADA
    RESERVADA --> CANCELADA
```
