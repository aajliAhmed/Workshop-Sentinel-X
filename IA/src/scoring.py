"""
Moteur de scoring de sécurité Sentinel-X.

Ce module reçoit les informations issues de la vision et des capteurs
et calcule un niveau de risque.
"""


# ============================================================
# CONFIGURATION DU SCORING
# ============================================================

PERSON_IN_PROTECTED_ZONE_POINTS = 3
PRESENCE_OVER_5S_POINTS = 2
ARMED_MODE_POINTS = 2
MULTIPLE_PERSONS_POINTS = 1
PIR_ACTIVE_POINTS = 2
PERSON_NEAR_BOX_POINTS = 1


# ============================================================
# NIVEAUX DE RISQUE
# ============================================================

def get_risk_level(score):
    """
    Convertit un score numérique en niveau de risque.
    """

    if score >= 6:
        return "CRITIQUE"

    if score >= 3:
        return "AVERTISSEMENT"

    return "INFO"


# ============================================================
# ACTION ASSOCIÉE AU NIVEAU
# ============================================================

def get_action(level):
    """
    Détermine l'action à effectuer selon le niveau de risque.
    """

    if level == "CRITIQUE":
        return "ALERT_BUZZER"

    if level == "AVERTISSEMENT":
        return "ALERT_LED_ORANGE"

    return "LOG_ONLY"


# ============================================================
# CALCUL DU SCORE
# ============================================================

def calculate_score(
    person_in_protected_zone=False,
    presence_over_5s=False,
    armed_mode=False,
    multiple_persons=False,
    pir_active=False,
    person_near_box=False
):
    """
    Calcule le score de risque Sentinel-X.

    Retourne :
        score
        level
        action
        reasons
    """

    score = 0
    reasons = []

    # --------------------------------------------------------
    # Personne dans la zone protégée
    # --------------------------------------------------------

    if person_in_protected_zone:
        score += PERSON_IN_PROTECTED_ZONE_POINTS

        reasons.append({
            "code": "PERSON_IN_PROTECTED_ZONE",
            "label": "Personne dans zone protégée",
            "points": PERSON_IN_PROTECTED_ZONE_POINTS
        })

    # --------------------------------------------------------
    # Présence supérieure à 5 secondes
    # --------------------------------------------------------

    if presence_over_5s:
        score += PRESENCE_OVER_5S_POINTS

        reasons.append({
            "code": "PRESENCE_OVER_5S",
            "label": "Présence supérieure à 5 secondes",
            "points": PRESENCE_OVER_5S_POINTS
        })

    # --------------------------------------------------------
    # Mode armé
    # --------------------------------------------------------

    if armed_mode:
        score += ARMED_MODE_POINTS

        reasons.append({
            "code": "ARMED_MODE",
            "label": "Mode armé",
            "points": ARMED_MODE_POINTS
        })

    # --------------------------------------------------------
    # Plusieurs personnes
    # --------------------------------------------------------

    if multiple_persons:
        score += MULTIPLE_PERSONS_POINTS

        reasons.append({
            "code": "MULTIPLE_PERSONS",
            "label": "Plusieurs personnes détectées",
            "points": MULTIPLE_PERSONS_POINTS
        })

    # --------------------------------------------------------
    # PIR
    # --------------------------------------------------------

    if pir_active:
        score += PIR_ACTIVE_POINTS

        reasons.append({
            "code": "PIR_ACTIVE",
            "label": "Détection PIR active",
            "points": PIR_ACTIVE_POINTS
        })

    # --------------------------------------------------------
    # Personne proche du boîtier
    # --------------------------------------------------------

    if person_near_box:
        score += PERSON_NEAR_BOX_POINTS

        reasons.append({
            "code": "PERSON_NEAR_BOX",
            "label": "Personne proche du boîtier",
            "points": PERSON_NEAR_BOX_POINTS
        })

    # --------------------------------------------------------
    # Niveau et action
    # --------------------------------------------------------

    level = get_risk_level(score)
    action = get_action(level)

    return {
        "score": score,
        "level": level,
        "action": action,
        "reasons": reasons
    }