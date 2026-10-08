from datetime import datetime, timezone
from pathlib import Path
import asyncio
import json
import os
import threading
import time

import paho.mqtt.client as mqtt

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="SENTINEL-X Backend",
    version="0.2.0",
    description="Backend local for SENTINEL-X security station",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# WEBSOCKET CLIENTS
# ============================================================

connected_clients: set[WebSocket] = set()

# ============================================================
# CURRENT AI SECURITY STATE
# ============================================================

last_security_event = None

# Event loop principal de FastAPI.
# MQTT fonctionne dans un thread différent.
main_loop = None


# ============================================================
# CAMERA / YOLO
# ============================================================

"""
Structure attendue :

SENTINEL-X/
│
├── backend/
│   └── main.py
│
├── IA/
│   ├── detect_person.py
│   └── latest_frame.jpg
│
└── dashboard/
    └── ...

Le chemin peut être changé avec la variable d'environnement :

SENTINEL_FRAME_PATH

Exemple Windows :

set SENTINEL_FRAME_PATH=C:\\...\\IA\\latest_frame.jpg
"""

DEFAULT_FRAME_PATH = (
    Path(__file__).resolve().parent.parent
    / "IA"
    / "latest_frame.jpg"
)

FRAME_PATH = Path(
    os.getenv(
        "SENTINEL_FRAME_PATH",
        str(DEFAULT_FRAME_PATH)
    )
)

print(f"[CAMERA] Frame path: {FRAME_PATH}")


# ============================================================
# MQTT CONFIGURATION
# ============================================================

MQTT_BROKER = os.getenv(
    "MQTT_BROKER",
    "localhost"
)

MQTT_PORT = int(
    os.getenv(
        "MQTT_PORT",
        "1883"
    )
)

MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC",
    "sentinel-x/telemetry"
)


# ============================================================
# WEBSOCKET BROADCAST
# ============================================================

async def broadcast(message: dict):
    """
    Envoie un message JSON à tous les dashboards connectés.
    """

    if not connected_clients:
        print("[WS] No connected dashboard clients")
        return

    print(
        f"[WS] Broadcasting to "
        f"{len(connected_clients)} client(s)"
    )

    print(
        "[WS] Message:",
        json.dumps(
            message,
            ensure_ascii=False,
            indent=2
        )
    )

    disconnected_clients = set()

    for websocket in list(connected_clients):

        try:

            await websocket.send_json(message)

        except Exception as error:

            print(
                f"[WS] Send error: {error}"
            )

            disconnected_clients.add(
                websocket
            )

    for websocket in disconnected_clients:

        connected_clients.discard(
            websocket
        )


# ============================================================
# MQTT CALLBACK - CONNECT
# ============================================================

def on_mqtt_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):

    print(
        f"[MQTT] Connected to broker "
        f"- reason_code={reason_code}"
    )

    result, mid = client.subscribe(
        MQTT_TOPIC
    )

    if result == mqtt.MQTT_ERR_SUCCESS:

        print(
            f"[MQTT] Subscribed to: "
            f"{MQTT_TOPIC}"
        )

    else:

        print(
            f"[MQTT] Subscription error: "
            f"{result}"
        )


# ============================================================
# MQTT CALLBACK - MESSAGE
# ============================================================

def on_mqtt_message(
    client,
    userdata,
    message
):

    print()
    print("=" * 60)
    print("[MQTT] Message received")
    print(
        f"[MQTT] Topic: {message.topic}"
    )

    try:

        payload = message.payload.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        print(
            "[MQTT] Invalid UTF-8 payload"
        )

        return

    print(
        f"[MQTT] Payload: {payload}"
    )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:

        telemetry = json.loads(
            payload
        )

    except json.JSONDecodeError:

        print(
            "[MQTT] Invalid JSON payload"
        )

        return

    # --------------------------------------------------------
    # MESSAGE FOR DASHBOARD
    # --------------------------------------------------------

    dashboard_message = {
        "type": "telemetry",
        "data": telemetry
    }

    print(
        "[MQTT] Forwarding telemetry "
        "to dashboard"
    )

    # --------------------------------------------------------
    # MQTT = THREAD DIFFERENT DE FASTAPI
    # --------------------------------------------------------

    if main_loop is None:

        print(
            "[MQTT] FastAPI event loop "
            "not ready"
        )

        return

    try:

        asyncio.run_coroutine_threadsafe(
            broadcast(
                dashboard_message
            ),
            main_loop
        )

    except Exception as error:

        print(
            f"[MQTT] Broadcast error: "
            f"{error}"
        )

    print("=" * 60)


# ============================================================
# MQTT CLIENT
# ============================================================

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="sentinel-x-backend",
)

mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_message = on_mqtt_message


# ============================================================
# MQTT THREAD
# ============================================================

def start_mqtt():

    print()
    print(
        "[MQTT] Starting MQTT subscriber..."
    )

    while True:

        try:

            print(
                f"[MQTT] Connecting to "
                f"{MQTT_BROKER}:{MQTT_PORT}..."
            )

            mqtt_client.connect(
                MQTT_BROKER,
                MQTT_PORT,
                keepalive=60,
            )

            print(
                "[MQTT] MQTT loop started"
            )

            mqtt_client.loop_forever()

        except Exception as error:

            print(
                f"[MQTT] Connection error: "
                f"{error}"
            )

            print(
                "[MQTT] Retry in 5 seconds..."
            )

            time.sleep(5)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():

    global main_loop

    main_loop = (
        asyncio.get_running_loop()
    )

    mqtt_thread = threading.Thread(
        target=start_mqtt,
        daemon=True,
        name="sentinel-x-mqtt"
    )

    mqtt_thread.start()

    print(
        "[MQTT] Subscriber thread started"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "sentinel-x-backend",
        "mqtt_broker": MQTT_BROKER,
        "mqtt_topic": MQTT_TOPIC,
        "camera_frame": str(
            FRAME_PATH
        ),
    }


# ============================================================
# WEBSOCKET - DASHBOARD
# ============================================================

@app.websocket("/ws/telemetry")
async def telemetry_websocket(
    websocket: WebSocket
):

    await websocket.accept()

    connected_clients.add(
        websocket
    )

    print(
        f"[WS] Dashboard connected "
        f"({len(connected_clients)} client(s))"
    )

    if last_security_event is not None:

        print(
            "[WS] Sending current AI security state"
        )

        try:

            await websocket.send_json({
                "type": "security_alert",
                "data": last_security_event,
            })

        except Exception as error:

            print(
                f"[WS] Initial state error: {error}"
            )

    try:

        while True:

            # Le dashboard garde la connexion
            # ouverte.
            #
            # Nous attendons simplement
            # d'éventuels messages du navigateur.

            await websocket.receive_text()

    except Exception as error:

        print(
            f"[WS] Dashboard connection "
            f"closed: {error}"
        )

    finally:

        connected_clients.discard(
            websocket
        )

        print(
            f"[WS] Dashboard disconnected "
            f"({len(connected_clients)} "
            f"client(s) remaining)"
        )


# ============================================================
# TEST TELEMETRY
# ============================================================

@app.post("/test/telemetry")
async def test_telemetry():

    telemetry = {

        "device_id":
            "SENTINEL-X-01",

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "temperature":
            28.3,

        "humidity":
            49.7,

        "motion":
            True,

        "gas":
            0,
    }

    message = {

        "type":
            "telemetry",

        "data":
            telemetry,
    }

    await broadcast(
        message
    )

    print(
        "[TEST] Telemetry sent:"
    )

    print(
        json.dumps(
            telemetry,
            indent=2,
            ensure_ascii=False
        )
    )

    return {
        "status": "sent",
        "telemetry": telemetry
    }


# ============================================================
# IA / SECURITY ALERTS
# ============================================================

@app.post("/api/v1/alerts")
async def receive_security_alert(
    event: dict
):

    print()
    print("=" * 60)
    print(
        "[IA] Security event received"
    )

    print(
        json.dumps(
            event,
            indent=2,
            ensure_ascii=False
        )
    )


    #--------------------------------------------------------
    # SAVE CURRENT AI STATE
    # --------------------------------------------------------

    last_security_event = event.copy()

    # --------------------------------------------------------
    # MESSAGE DASHBOARD
    # --------------------------------------------------------

    message = {

        "type":
            "security_alert",

        "data":
            event,
    }

    # --------------------------------------------------------
    # WEBSOCKET
    # --------------------------------------------------------

    print(
        "[IA] Forwarding security event "
        "to dashboard"
    )

    await broadcast(
        message
    )

    print(
        "[IA] Security event broadcasted"
    )

    print("=" * 60)

    return {

        "status":
            "accepted",

        "event":
            event.get(
                "event"
            ),
    }


# ============================================================
# CAMERA STATUS
# ============================================================

@app.get("/api/v1/camera/status")
async def camera_status():

    exists = FRAME_PATH.exists()

    if exists:

        try:

            modified_time = (
                FRAME_PATH.stat().st_mtime
            )

            age = (
                time.time()
                - modified_time
            )

        except Exception:

            age = None

    else:

        age = None

    return {

        "camera": "UGREEN",

        "frame_path":
            str(FRAME_PATH),

        "frame_exists":
            exists,

        "frame_age_seconds":
            age,

        "status":
            "online"
            if exists
            else "waiting",
    }


# ============================================================
# CAMERA MJPEG STREAM
# ============================================================

def camera_stream():

    """
    Génère un flux MJPEG à partir de
    latest_frame.jpg.

    YOLO met à jour cette image.
    FastAPI la diffuse au Dashboard.
    """

    print(
        "[CAMERA] Client connected "
        "to camera stream"
    )

    while True:

        if not FRAME_PATH.exists():

            time.sleep(0.1)

            continue

        try:

            frame = (
                FRAME_PATH
                .read_bytes()
            )

            if not frame:

                time.sleep(0.05)

                continue

            yield (

                b"--frame\r\n"

                b"Content-Type: "
                b"image/jpeg\r\n\r\n"

                + frame

                + b"\r\n"
            )

        except Exception as error:

            print(
                "[CAMERA] Frame read error:",
                error
            )

            time.sleep(0.1)

            continue

        # Environ 12-15 images/s maximum.
        time.sleep(0.08)


@app.get("/api/v1/camera/stream")
def camera_video_stream():

    return StreamingResponse(

        camera_stream(),

        media_type=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        ),

        headers={
            "Cache-Control":
                "no-cache, no-store, must-revalidate",

            "Pragma":
                "no-cache",

            "Expires":
                "0",
        },
    )


# ============================================================
# CAMERA - SINGLE FRAME
# ============================================================

@app.get("/api/v1/camera/frame")
async def camera_frame():

    """
    Retourne simplement la dernière image
    YOLO disponible.
    """

    if not FRAME_PATH.exists():

        return {
            "status":
                "waiting",

            "message":
                "No YOLO frame available yet.",
        }

    try:

        frame = (
            FRAME_PATH
            .read_bytes()
        )

        from fastapi.responses import Response

        return Response(
            content=frame,
            media_type="image/jpeg",
            headers={
                "Cache-Control":
                    "no-cache, no-store, must-revalidate",
            },
        )

    except Exception as error:

        return {
            "status":
                "error",

            "message":
                str(error),
        }