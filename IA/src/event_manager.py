"""
Gestionnaire d'événements de sécurité Sentinel-X.

Ce module gère les changements d'état d'une présence humaine
afin d'éviter les événements dupliqués et de détecter les
escalades de risque.
"""

import time


class EventManager:

    def __init__(
        self,
        presence_threshold=5.0,
        absence_threshold=1.0
    ):
        """
        Args:
            presence_threshold (float):
                Durée nécessaire avant de considérer la présence
                comme une situation critique.

            absence_threshold (float):
                Durée d'absence nécessaire avant de considérer
                que la personne a réellement quitté la zone.
        """

        self.presence_threshold = presence_threshold
        self.absence_threshold = absence_threshold

        self.person_present = False
        self.presence_start_time = None
        self.last_detection_time = None

        self.alert_sent = False

    def update(self, person_detected):
        """
        Met à jour l'état du gestionnaire.

        Args:
            person_detected (bool):
                True si une personne est actuellement détectée.

        Returns:
            str | None:
                Type d'événement à générer, ou None.
        """

        now = time.perf_counter()

        # --------------------------------------------------
        # PERSONNE DÉTECTÉE
        # --------------------------------------------------

        if person_detected:

            self.last_detection_time = now

            # Nouvelle présence
            if not self.person_present:

                self.person_present = True
                self.presence_start_time = now
                self.alert_sent = False

                return "PERSON_DETECTED"

            # Présence déjà connue
            if self.presence_start_time is not None:

                presence_duration = (
                    now - self.presence_start_time
                )

                # Escalade après 5 secondes
                if (
                    presence_duration >= self.presence_threshold
                    and not self.alert_sent
                ):
                    self.alert_sent = True

                    return "RISK_ESCALATED"

            return None

        # --------------------------------------------------
        # PERSONNE NON DÉTECTÉE
        # --------------------------------------------------

        if self.person_present:

            if self.last_detection_time is not None:

                absence_duration = (
                    now - self.last_detection_time
                )

                # On tolère une perte temporaire de détection
                if absence_duration >= self.absence_threshold:

                    self.person_present = False
                    self.presence_start_time = None
                    self.last_detection_time = None
                    self.alert_sent = False

                    return "PERSON_CLEARED"

        return None

    def get_presence_duration(self):
        """
        Retourne la durée actuelle de présence.

        Returns:
            float:
                Durée en secondes.
        """

        if (
            self.person_present
            and self.presence_start_time is not None
        ):
            return time.perf_counter() - self.presence_start_time

        return 0.0