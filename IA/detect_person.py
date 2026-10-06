import cv2
import time
from ultralytics import YOLO
import sys
from pathlib import Path


# Importation fonction calculate_score
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from scoring import calculate_score


# ============================================================
# CONFIGURATION SENTINEL-X
# ============================================================

CAMERA_INDEX = 0
MODEL_PATH = "yolov8n.pt"

# Seuil de confiance minimum
CONFIDENCE_THRESHOLD = 0.50

# Mode sécurité activé (pendant la nuit par exemple)
ARMED_MODE = True

# Durée avant de considérer la présence comme persistante
PRESENCE_THRESHOLD_SECONDS = 5.0

# fixation de la Zone protégée
# Format : x1, y1, x2, y2
PROTECTED_ZONE = {
    "x1": 100,
    "y1": 80,
    "x2": 540,
    "y2": 450
}

## detecter si le centre de la personne est bien dans la zone protégée
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


# Variable permettant de mémoriser le début de présence
presence_start_time = None


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
    # Capture image
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

        # Coordonnées du rectangle
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

        persons.append(person)
        if is_person_in_protected_zone(person):
            person["in_protected_zone"] = True
        else:
            person["in_protected_zone"] = False


    person_in_protected_zone = any(
    person["in_protected_zone"]
    for person in persons)

    # Gestion de la durée de présence dans la zone protégée
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
    presence_over_5s = presence_duration >= PRESENCE_THRESHOLD_SECONDS

    

    multiple_persons = person_count > 1
    
    score_result = calculate_score(
        person_in_protected_zone=person_in_protected_zone,
        presence_over_5s=presence_over_5s,
        armed_mode=ARMED_MODE,
        multiple_persons=multiple_persons,
        pir_active=False,
        person_near_box=False
    )

    

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
        2)
        
    cv2.putText(
        annotated_frame,
        f"Risque : {score_result['level']}",
        (20, 285),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2)
    


    # --------------------------------------------------------
    # AFFICHAGE
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
    2)
    
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
    2)

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