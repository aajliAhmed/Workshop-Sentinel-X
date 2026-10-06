from datetime import datetime, timezone
import json

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="SENTINEL-X Backend",
    version="0.1.0",
    description="Backend local for SENTINEL-X security station",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# WEBSOCKET CLIENTS
# ============================================================

connected_clients: set[WebSocket] = set()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "sentinel-x-backend",
    }


# ============================================================
# WEBSOCKET - TELEMETRY
# ============================================================

@app.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket):

    await websocket.accept()

    connected_clients.add(websocket)

    print("[WS] Dashboard connected")

    try:
        while True:
            # Le Dashboard garde la connexion ouverte.
            # Nous attendons simplement un message éventuel.
            await websocket.receive_text()

    except Exception:
        pass

    finally:
        connected_clients.discard(websocket)

        print("[WS] Dashboard disconnected")


# ============================================================
# TEST TELEMETRY
# ============================================================

@app.post("/test/telemetry")
async def test_telemetry():

    telemetry = {
        "device_id": "SENTINEL-X-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),

        # Vraies valeurs de test
        "temperature": 28.3,
        "humidity": 49.7,

        # PIR
        "motion": True,

        # MQ-2 pas encore installé
        "gas": 0,
    }

    message = json.dumps(telemetry)

    disconnected_clients = []

    for client in connected_clients:

        try:
            await client.send_text(message)

        except Exception:
            disconnected_clients.append(client)

    for client in disconnected_clients:
        connected_clients.discard(client)

    print("[TEST] Telemetry sent:")
    print(telemetry)

    return telemetry