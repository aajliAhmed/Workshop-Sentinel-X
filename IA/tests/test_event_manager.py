import sys
from pathlib import Path
import time

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from event_manager import EventManager


print("========================================")
print(" TEST EVENT MANAGER SENTINEL-X")
print("========================================")


manager = EventManager(
    presence_threshold=5.0,
    absence_threshold=1.0
)


# --------------------------------------------------
# TEST 1 : aucune personne
# --------------------------------------------------

print("\n[TEST 1] Aucune personne")

event = manager.update(False)

print("Événement :", event)

assert event is None


# --------------------------------------------------
# TEST 2 : nouvelle personne
# --------------------------------------------------

print("\n[TEST 2] Nouvelle personne détectée")

event = manager.update(True)

print("Événement :", event)

assert event == "PERSON_DETECTED"


# --------------------------------------------------
# TEST 3 : personne toujours présente
# --------------------------------------------------

print("\n[TEST 3] Personne toujours présente")

event = manager.update(True)

print("Événement :", event)

assert event is None


# --------------------------------------------------
# TEST 4 : simulation de 5 secondes
# --------------------------------------------------

print("\n[TEST 4] Présence supérieure à 5 secondes")

manager.presence_start_time -= 5.1

event = manager.update(True)

print("Événement :", event)

assert event == "RISK_ESCALATED"


# --------------------------------------------------
# TEST 5 : aucune répétition de l'alerte critique
# --------------------------------------------------

print("\n[TEST 5] Pas de répétition de l'escalade")

event = manager.update(True)

print("Événement :", event)

assert event is None


# --------------------------------------------------
# TEST 6 : perte temporaire de détection
# --------------------------------------------------

print("\n[TEST 6] Perte temporaire de détection")

event = manager.update(False)

print("Événement :", event)

assert event is None


# --------------------------------------------------
# TEST 7 : retour de la personne
# --------------------------------------------------

print("\n[TEST 7] Personne retrouvée rapidement")

event = manager.update(True)

print("Événement :", event)

assert event is None


# --------------------------------------------------
# TEST 8 : disparition réelle
# --------------------------------------------------

print("\n[TEST 8] Disparition réelle")

manager.last_detection_time -= 1.1

event = manager.update(False)

print("Événement :", event)

assert event == "PERSON_CLEARED"


# --------------------------------------------------
# FIN
# --------------------------------------------------

print("\n========================================")
print(" TOUS LES TESTS SONT RÉUSSIS")
print("========================================")