"""
Gestion des événements de sécurité Sentinel-X.

Ce module transforme les changements d'état détectés
par EventManager en événements structurés pouvant être
transmis au backend et à l'interface React.
"""

from datetime import datetime, timezone


def create_security_event(
    event_type,
    score_result,
    person_count=0,
    person_in_protected_zone=False,
    presence_duration=0.0,
):
    """
    Crée un événement de sécurité structuré.

    Args:
        event_type (str):
            Type d'événement :
            PERSON_DETECTED
            RISK_ESCALATED
            PERSON_CLEARED

        score_result (dict):
            Résultat retourné par calculate_score().

        person_count (int):
            Nombre de personnes détectées.

        person_in_protected_zone (bool):
            Indique si une personne est dans la zone protégée.

        presence_duration (float):
            Durée de présence en secondes.

    Returns:
        dict: événement de sécurité.
    """

    return {
        "type": "security_alert",
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "score": score_result["score"],
        "level": score_result["level"],
        "action": score_result["action"],

        "person_count": person_count,
        "person_in_protected_zone": person_in_protected_zone,
        "presence_duration": round(presence_duration, 2),

        "reasons": score_result["reasons"],
    }