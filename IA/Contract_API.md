# Sentinel-X — Contrat API IA / Backend (Interface)

## 1. Rôle du module IA

Le module IA Sentinel-X est responsable de :

- capturer les images depuis la caméra USB ;
- détecter les personnes avec YOLO ;
- déterminer si une personne se trouve dans la zone protégée ;
- mesurer la durée de présence ;
- calculer le score de risque et déterminer le niveau correspondant;
- générer un événement de sécurité.

Le backend de l'interface web est responsable de recevoir et exploiter ces événements.

Architecture :

```text
Webcam USB
    ↓
YOLO
    ↓
EventManager
    ↓
Scoring
    ↓
Security Event
    ↓
sender.py
    ↓
POST /api/v1/alerts
    ↓
Backend FastAPI
    ↓
React Dashboard