import cv2
import time
from ultralytics import YOLO
import sys
from pathlib import Path


# Importation des fonctions Sentinel-X
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from scoring import calculate_score
from events import create_security_event
from sender import send_event
from event_manager import EventManager


# ============================================================
# CONFIGURATION SENTINEL-X
# ============================================================

CAMERA_INDEX = 0
MODEL_PATH = "yolov8n.pt"

# Seuil de confiance minimum
CONFIDENCE_THRESHOLD = 0.50

# Mode sécurité activé
ARMED_MODE = True

# Durée avant de considérer la présence comme persistante
PRESENCE_THRESHOLD_SECONDS = 5.0

event_manager = EventManager(
    presence_threshold=PRESENCE_THRESHOLD_SECONDS,
    absence_threshold=1.0
)

# Zone protégée
# Format : x1, y1, x2, y2
PROTECTED_ZONE = {
    "x1": 100,
    "y1": 80,
    "x2": 540,
    "y2": 450
}


# ============================================================
# DETECTION ZONE PROTEGEE
# ============================================================

def is_person_in_protected_zone(person):
    """
    Vérifie si le centre de la bounding box
    d'une personne se trouve dans la zone protégée.
    """

    center_x = (person["x1"] + person["x2"]) // 2
    center_y = (person["y1"] + person["y2"]) // 2

    return (
        PROTECTED_ZONE["x1"] <= center_x <= PROTECTED_ZONE["x2"]
        and
        PROTECTED_ZONE["y1"] <= center_y <= PROTECTED_ZONE["y2"]
    )


# ============================================================
# VARIABLES D'ETAT
# ============================================================

# Début de présence dans la zone protégée
presence_start_time = None

# Permet de détecter une nouvelle apparition
person_was_detected = False


# ============================================================
# CHARGEMENT YOLO
# ============================================================

print("[INFO] Chargement du modèle YOLO...")

model = YOLO(MODEL_PATH)

print("[INFO] Modèle YOLO chargé.")


# ============================================================
# OUVERTURE CAMERA UGREEN
# ============================================================

print(f"[INFO] Ouverture caméra index {CAMERA_INDEX}...")

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("[ERREUR] Impossible d'ouvrir la caméra.")
    exit()

print("[INFO] Caméra UGREEN OK.")
print("[INFO] Appuyez sur Q pour quitter.")


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

while True:

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # CAPTURE IMAGE
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:
        print("[ERREUR] Impossible de lire une image.")
        break

    # --------------------------------------------------------
    # INFERENCE YOLO
    # --------------------------------------------------------

    results = model(
        frame,
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )

    result = results[0]

    # --------------------------------------------------------
    # VARIABLES SENTINEL-X
    # --------------------------------------------------------

    person_count = 0
    persons = []

    # --------------------------------------------------------
    # ANALYSE DES DETECTIONS
    # --------------------------------------------------------

    for box in result.boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        # Classe COCO 0 = personne
        if class_id != 0:
            continue

        person_count += 1

        # Coordonnées de la bounding box
        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )

        person = {
            "confidence": confidence,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }

        person["in_protected_zone"] = (
            is_person_in_protected_zone(person)
        )

        persons.append(person)

    # --------------------------------------------------------
    # DETECTION DANS LA ZONE PROTEGEE
    # --------------------------------------------------------

    person_in_protected_zone = any(
        person["in_protected_zone"]
        for person in persons
    )

    # --------------------------------------------------------
    # GESTION DE LA DUREE DE PRESENCE
    # --------------------------------------------------------

    if person_in_protected_zone:

        if presence_start_time is None:
            presence_start_time = time.perf_counter()

    else:

        presence_start_time = None

    presence_duration = (
        time.perf_counter() - presence_start_time
        if presence_start_time is not None
        else 0.0
    )

    presence_over_5s = (
        presence_duration >= PRESENCE_THRESHOLD_SECONDS
    )

    # --------------------------------------------------------
    # CALCUL DU SCORE
    # --------------------------------------------------------

    multiple_persons = person_count > 1

    score_result = calculate_score(
        person_in_protected_zone=person_in_protected_zone,
        presence_over_5s=presence_over_5s,
        armed_mode=(ARMED_MODE
                    if person_in_protected_zone
                    else False),
        multiple_persons=multiple_persons,
        pir_active=False,
        person_near_box=False
    )

    # --------------------------------------------------------
    # DETECTION D'UNE NOUVELLE PRESENCE
    # --------------------------------------------------------

    person_detected = person_count > 0
    
    event_type = event_manager.update(person_detected)
    
    if event_type is not None:
        
        presence_duration = event_manager.get_presence_duration()
        
        # Recalcul du score selon le type d'événement
       # Recalcul du score selon le type d'événement
        presence_over_5s = event_type == "RISK_ESCALATED"
        
    # Le mode armé ne doit contribuer au score
    # # que lorsqu'une présence humaine constitue réellement
    # # un événement de sécurité.
        armed_mode_for_event = (
             ARMED_MODE
             if event_type in ["PERSON_DETECTED", "RISK_ESCALATED"]
             and person_in_protected_zone
             else False
             )
        
        score_result = calculate_score(
            person_in_protected_zone=person_in_protected_zone,
            presence_over_5s=presence_over_5s,
            armed_mode=armed_mode_for_event,
            multiple_persons=multiple_persons,
            pir_active=False,
            person_near_box=False
            )
        
        security_event = create_security_event(
            event_type=event_type,
            score_result=score_result,
            person_count=person_count,
            person_in_protected_zone=person_in_protected_zone,
            presence_duration=presence_duration
            )
        
        print("\n[EVENT] Événement de sécurité :")
        print(security_event)
        send_event(security_event)

    # --------------------------------------------------------
    # ETAT SENTINEL-X
    # --------------------------------------------------------

    if person_count > 0:

        alert = True
        status = "INTRUS DETECTE"

    else:

        alert = False
        status = "ZONE SECURISEE"

    # --------------------------------------------------------
    # AFFICHAGE YOLO
    # --------------------------------------------------------

    annotated_frame = result.plot()

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    elapsed = time.perf_counter() - start_time

    latency_ms = elapsed * 1000

    if elapsed > 0:
        fps = 1 / elapsed
    else:
        fps = 0

    # --------------------------------------------------------
    # AFFICHAGE INFORMATIONS
    # --------------------------------------------------------

    cv2.putText(
        annotated_frame,
        f"STATUT : {status}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 0) if not alert else (0, 0, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Personnes : {person_count}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"FPS : {fps:.1f}",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Latence : {latency_ms:.1f} ms",
        (10, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Score : {score_result['score']}",
        (20, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Risque : {score_result['level']}",
        (20, 285),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Presence zone : {presence_duration:.1f}s",
        (20, 320),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # --------------------------------------------------------
    # AFFICHAGE ZONE PROTEGEE
    # --------------------------------------------------------

    cv2.rectangle(
        annotated_frame,
        (
            PROTECTED_ZONE["x1"],
            PROTECTED_ZONE["y1"]
        ),
        (
            PROTECTED_ZONE["x2"],
            PROTECTED_ZONE["y2"]
        ),
        (255, 255, 0),
        2
    )

    cv2.putText(
        annotated_frame,
        "ZONE PROTEGEE",
        (
            PROTECTED_ZONE["x1"],
            PROTECTED_ZONE["y1"] - 10
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    # --------------------------------------------------------
    # AFFICHAGE
    # --------------------------------------------------------

    cv2.imshow(
        "SENTINEL-X - Detection Personne",
        annotated_frame
    )

    # --------------------------------------------------------
    # SORTIE
    # --------------------------------------------------------

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# NETTOYAGE
# ============================================================

cap.release()
cv2.destroyAllWindows()

print("[INFO] SENTINEL-X arrêté.")