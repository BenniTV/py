"""
PyDispatch Leitstelle – Alarm-Service.
Kernlogik der Alarmierung: primäre Alarmierung, Fallback, Einsatz-Erstellung.
"""

from datetime import datetime

from leitstelle.database.connection import db
from leitstelle.services.status_service import StatusService


class AlarmService:
    """Service für die Alarmierungs-Logik."""

    @staticmethod
    def create_einsatz(stichwort_id: int, standort_text: str = None,
                       standort_id: int = None, leitstelle_db_id: int = None,
                       notiz: str = "") -> tuple[bool, str, int | None]:
        """
        Erstellt einen neuen Einsatz in der Datenbank.

        Returns:
            (success, message, einsatz_id)
        """
        try:
            einsatz_id = db.execute_insert(
                "INSERT INTO einsaetze (stichwort_id, standort_text, standort_id, "
                "leitstelle_id, notiz) "
                "VALUES (%s, %s, %s, %s, %s)",
                (stichwort_id, standort_text, standort_id, leitstelle_db_id, notiz)
            )
            return True, "Einsatz erstellt.", einsatz_id
        except Exception as e:
            return False, f"Fehler beim Erstellen des Einsatzes: {e}", None

    @staticmethod
    def alarmieren(stichwort_id: int, standort_text: str = None,
                   standort_id: int = None, leitstelle_db_id: int = None,
                   notiz: str = "") -> tuple[bool, str, dict]:
        """
        Führt die vollständige Alarmierung durch:
        1. Einsatz erstellen
        2. Primäre Alarmierung (aktive Gruppe, Status 'in_der_schule')
        3. Fallback: Alle User, wenn niemand in der Gruppe verfügbar

        Returns:
            (success, message, result_dict)
        """
        result = {
            "einsatz_id": None,
            "alarm_typ": None,       # "primaer" | "fallback" | "keine"
            "alarmierte_user": [],
            "gruppe_name": None,
        }

        # 1. Einsatz erstellen
        success, msg, einsatz_id = AlarmService.create_einsatz(
            stichwort_id, standort_text, standort_id, leitstelle_db_id, notiz
        )
        if not success:
            return False, msg, result

        result["einsatz_id"] = einsatz_id

        # 2. Aktive Gruppe prüfen
        active_group = StatusService.get_active_group()
        if active_group:
            result["gruppe_name"] = active_group["name"]

        # 3. Primäre Alarmierung: verfügbare Sanitäter der aktiven Gruppe
        available = StatusService.get_available_sanitaeter()

        if available:
            result["alarm_typ"] = "primaer"
            result["alarmierte_user"] = available
            return True, (
                f"Alarm ausgelöst! {len(available)} Sanitäter der Gruppe "
                f"'{active_group['name']}' alarmiert."
            ), result

        # 4. Fallback: ALLE aktiven Benutzer alarmieren
        all_users = StatusService.get_all_active_users()
        fallback_available = [
            u for u in all_users if u.get("status") == "in_der_schule"
        ]

        if fallback_available:
            result["alarm_typ"] = "fallback"
            result["alarmierte_user"] = fallback_available
            gruppe_text = f"Gruppe '{active_group['name']}'" if active_group else "der aktiven Gruppe"
            return True, (
                f"⚠ Kein Sanitäter in {gruppe_text} verfügbar!\n"
                f"Fallback: {len(fallback_available)} Sanitäter aus allen Gruppen alarmiert."
            ), result

        # 5. Keiner verfügbar
        result["alarm_typ"] = "keine"
        return True, (
            "🚫 KEINER VERFÜGBAR!\n\n"
            "Es ist kein Sanitäter verfügbar.\n"
            "Bitte veranlassen Sie alternative Maßnahmen."
        ), result

    @staticmethod
    def get_active_einsaetze() -> list[dict]:
        """Gibt alle aktiven (laufenden) Einsätze zurück."""
        try:
            return db.execute(
                "SELECT e.id, e.stichwort_id, e.standort_text, e.standort_id, "
                "e.alarmiert_am, e.status, e.notiz, "
                "sw.kuerzel, sw.bezeichnung, "
                "s.name AS standort_name "
                "FROM einsaetze e "
                "JOIN stichwoerter sw ON e.stichwort_id = sw.id "
                "LEFT JOIN standorte s ON e.standort_id = s.id "
                "WHERE e.status = 'aktiv' "
                "ORDER BY e.alarmiert_am DESC"
            )
        except Exception:
            return []

    @staticmethod
    def get_einsatz_history(limit: int = 50) -> list[dict]:
        """Gibt die letzten Einsätze zurück."""
        try:
            return db.execute(
                "SELECT e.id, e.stichwort_id, e.standort_text, e.standort_id, "
                "e.alarmiert_am, e.beendet_am, e.status, e.notiz, "
                "sw.kuerzel, sw.bezeichnung, "
                "s.name AS standort_name "
                "FROM einsaetze e "
                "JOIN stichwoerter sw ON e.stichwort_id = sw.id "
                "LEFT JOIN standorte s ON e.standort_id = s.id "
                "ORDER BY e.alarmiert_am DESC "
                "LIMIT %s",
                (limit,)
            )
        except Exception:
            return []

    @staticmethod
    def end_einsatz(einsatz_id: int) -> tuple[bool, str]:
        """Beendet einen aktiven Einsatz."""
        try:
            db.execute_modify(
                "UPDATE einsaetze SET status = 'beendet', beendet_am = NOW() "
                "WHERE id = %s AND status = 'aktiv'",
                (einsatz_id,)
            )
            return True, "Einsatz beendet."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def cancel_einsatz(einsatz_id: int) -> tuple[bool, str]:
        """Bricht einen aktiven Einsatz ab."""
        try:
            db.execute_modify(
                "UPDATE einsaetze SET status = 'abgebrochen', beendet_am = NOW() "
                "WHERE id = %s AND status = 'aktiv'",
                (einsatz_id,)
            )
            return True, "Einsatz abgebrochen."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def count_active_einsaetze() -> int:
        """Zählt die aktiven Einsätze."""
        try:
            results = db.execute(
                "SELECT COUNT(*) AS cnt FROM einsaetze WHERE status = 'aktiv'"
            )
            return results[0]["cnt"] if results else 0
        except Exception:
            return 0

    @staticmethod
    def count_total_einsaetze() -> int:
        """Zählt alle Einsätze."""
        try:
            results = db.execute("SELECT COUNT(*) AS cnt FROM einsaetze")
            return results[0]["cnt"] if results else 0
        except Exception:
            return 0
