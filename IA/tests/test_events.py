import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from scoring import calculate_score
from events import create_security_event


print("========================================")
print(" TEST EVENTS SENTINEL-X")
print("========================================")


# --------------------------------------------------
# TEST 1 : PERSON_DETECTED
# --------------------------------------------------

print("\n[TEST 1] PERSON_DETECTED")

score_result = calculate_score(
    person_in_protected_zone=True,
    presence_over_5s=False,
    armed_mode=True,
    multiple_persons=False,
    pir_active=False,
    person_near_box=False
)

event = create_security_event(
    event_type="PERSON_DETECTED",
    score_result=score_result,
    person_count=1,
    person_in_protected_zone=True,
    presence_duration=0.0
)

print(event)

assert event["event"] == "PERSON_DETECTED"
assert event["score"] == 5
assert event["level"] == "AVERTISSEMENT"
assert event["action"] == "ALERT_LED_ORANGE"


# --------------------------------------------------
# TEST 2 : RISK_ESCALATED
# --------------------------------------------------

print("\n[TEST 2] RISK_ESCALATED")

score_result = calculate_score(
    person_in_protected_zone=True,
    presence_over_5s=True,
    armed_mode=True,
    multiple_persons=False,
    pir_active=False,
    person_near_box=False
)

event = create_security_event(
    event_type="RISK_ESCALATED",
    score_result=score_result,
    person_count=1,
    person_in_protected_zone=True,
    presence_duration=5.03
)

print(event)

assert event["event"] == "RISK_ESCALATED"
assert event["score"] == 7
assert event["level"] == "CRITIQUE"
assert event["action"] == "ALERT_BUZZER"
assert event["presence_duration"] == 5.03


# --------------------------------------------------
# TEST 3 : PERSON_CLEARED
# --------------------------------------------------

print("\n[TEST 3] PERSON_CLEARED")

score_result = calculate_score()

event = create_security_event(
    event_type="PERSON_CLEARED",
    score_result=score_result,
    person_count=0,
    person_in_protected_zone=False,
    presence_duration=0.0
)

print(event)

assert event["event"] == "PERSON_CLEARED"
assert event["score"] == 0
assert event["level"] == "INFO"
assert event["action"] == "LOG_ONLY"


# --------------------------------------------------
# FIN
# --------------------------------------------------

print("\n========================================")
print(" TOUS LES TESTS SONT RÉUSSIS")
print("========================================")