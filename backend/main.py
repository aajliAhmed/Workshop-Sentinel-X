from datetime import datetime, timezone
import json
import asyncio
import threading

import paho.mqtt.client as mqtt

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
main_loop = None
# ============================================================
# MQTT
# ============================================================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sentinel-x/telemetry"

def on_mqtt_connect(client, userdata, flags, reason_code, properties):
    print(f"[MQTT] Connected to broker - reason_code={reason_code}")

    client.subscribe(MQTT_TOPIC)

    print(f"[MQTT] Subscribed to: {MQTT_TOPIC}")

async def broadcast_telemetry(message: str):

    disconnected_clients = []

    for websocket in list(connected_clients):

        try:
            await websocket.send_text(message)

        except Exception as error:
            print(f"[WS] Send error: {error}")
            disconnected_clients.append(websocket)

    for websocket in disconnected_clients:
        connected_clients.discard(websocket)

def on_mqtt_message(client, userdata, message):

    payload = message.payload.decode("utf-8")

    print("[MQTT] Message received")
    print(f"[MQTT] Topic: {message.topic}")
    print(f"[MQTT] Payload: {payload}")

    try:
        telemetry = json.loads(payload)

    except json.JSONDecodeError:
        print("[MQTT] Invalid JSON payload")
        return

    print("[MQTT] Forwarding telemetry to dashboard")

    if main_loop is None:
        print("[MQTT] FastAPI event loop not ready")
        return

    asyncio.run_coroutine_threadsafe(
        broadcast_telemetry(
            json.dumps(telemetry)
        ),
        main_loop,
    )

    payload = message.payload.decode("utf-8")

    print("[MQTT] Message received")
    print(f"[MQTT] Topic: {message.topic}")
    print(f"[MQTT] Payload: {payload}")

    try:
        telemetry = json.loads(payload)

    except json.JSONDecodeError:
        print("[MQTT] Invalid JSON payload")
        return

    # Envoyer la télémétrie aux dashboards connectés
    disconnected_clients = []

    for websocket in connected_clients:

        try:
            # IMPORTANT :
            # MQTT tourne dans un thread différent de FastAPI.
            # Cette partie sera sécurisée dans l'étape suivante.
            print("[MQTT] Forwarding telemetry to dashboard")

        except Exception as error:
            print(f"[MQTT] WebSocket error: {error}")
            disconnected_clients.append(websocket)

    for websocket in disconnected_clients:
        connected_clients.discard(websocket)

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="sentinel-x-backend",
)

mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_message = on_mqtt_message

def start_mqtt():

    print("[MQTT] Connecting to broker...")

    mqtt_client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        keepalive=60,
    )

    mqtt_client.loop_forever()

@app.on_event("startup")
async def startup_event():

    global main_loop

    main_loop = asyncio.get_running_loop()

    mqtt_thread = threading.Thread(
        target=start_mqtt,
        daemon=True,
    )

    mqtt_thread.start()

    print("[MQTT] Subscriber thread started")


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