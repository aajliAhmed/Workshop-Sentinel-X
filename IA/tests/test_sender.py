import sys
from pathlib import Path

# Permet d'importer les modules situés dans ../src
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from sender import send_event


print("========================================")
print(" TEST SENDER SENTINEL-X")
print("========================================")


test_event = {
    "type": "security_alert",
    "timestamp": "2026-10-07T10:00:00+02:00",
    "score": 7,
    "level": "CRITIQUE",
    "action": "ALERT_BUZZER",
    "person_count": 1,
    "person_in_protected_zone": True,
    "presence_duration": 6.42,
    "reasons": [
        {
            "code": "PERSON_IN_PROTECTED_ZONE",
            "label": "Personne dans zone protégée",
            "points": 3
        }
    ]
}


print("\n[TEST] Envoi de l'événement...")

success = send_event(test_event)

print("\n[RESULTAT]")

if success:
    print("Test réussi.")
else:
    print("Test échoué.")