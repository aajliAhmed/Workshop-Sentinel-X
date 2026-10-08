import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from scoring import calculate_score


print("========================================")
print(" TEST SCORING SENTINEL-X")
print("========================================")


# ------------------------------------------------------------
# TEST 1 : Aucun événement
# ------------------------------------------------------------

result = calculate_score()

print("\nTEST 1")
print(result)


# ------------------------------------------------------------
# TEST 2 : Personne dans la zone
# ------------------------------------------------------------

result = calculate_score(
    person_in_protected_zone=True
)

print("\nTEST 2")
print(result)


# ------------------------------------------------------------
# TEST 3 : Intrusion critique
# ------------------------------------------------------------

result = calculate_score(
    person_in_protected_zone=True,
    presence_over_5s=True,
    armed_mode=True,
    pir_active=True
)

print("\nTEST 3")
print(result)