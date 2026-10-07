"""
Envoi des événements de sécurité Sentinel-X vers le backend.

Ce module est responsable de la communication HTTP
entre le module IA (detection des personnes) et le backend.
"""

import requests


# Configuration du backend

BACKEND_URL = "http://localhost:8000"
ALERT_ENDPOINT = "/api/v1/alerts"


def send_event(event):
    """
    Envoie un événement de sécurité au backend.

    Args:
        event (dict):
            Événement créé par events.py.

    Returns:
        bool:
            True si l'événement a été accepté par le backend,
            False en cas d'erreur.
    """

    url = f"{BACKEND_URL}{ALERT_ENDPOINT}"

    try:
        response = requests.post(
            url,
            json=event,
            timeout=2
        )

        if response.status_code == 200:
            print("[API] Événement envoyé au backend.")
            return True

        print(
            f"[API] Erreur backend : "
            f"HTTP {response.status_code}"
        )
        return False

    except requests.RequestException as error:
        print(f"[API] Backend inaccessible : {error}")
        return False