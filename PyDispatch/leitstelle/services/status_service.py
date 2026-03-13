"""
PyDispatch Leitstelle – Gruppen- und Status-Service.
Liest aktive Gruppe, verfügbare Sanitäter etc.
"""

from leitstelle.database.connection import db


class StatusService:
    """Service für Status-Abfragen der Leitstelle."""

    @staticmethod
    def get_active_group() -> dict | None:
        """Gibt die aktuell aktive Benutzergruppe zurück."""
        try:
            results = db.execute(
                "SELECT bg.id, bg.name, bg.beschreibung "
                "FROM aktive_gruppe ag "
                "JOIN benutzergruppen bg ON ag.gruppen_id = bg.id "
                "WHERE ag.id = 1"
            )
            return results[0] if results else None
        except Exception:
            return None

    @staticmethod
    def get_available_sanitaeter() -> list[dict]:
        """Gibt Sanitäter zurück, die 'in_der_schule' sind und zur aktiven Gruppe gehören."""
        try:
            active_group = StatusService.get_active_group()
            if not active_group:
                return []

            return db.execute(
                "SELECT b.id, b.benutzername, b.vorname, b.nachname, b.status "
                "FROM benutzer b "
                "JOIN benutzer_gruppen bg ON b.id = bg.benutzer_id "
                "WHERE bg.gruppen_id = %s "
                "AND b.ist_aktiv = TRUE "
                "AND b.status = 'in_der_schule' "
                "ORDER BY b.nachname, b.vorname",
                (active_group["id"],)
            )
        except Exception:
            return []

    @staticmethod
    def get_all_group_members() -> list[dict]:
        """Gibt alle Mitglieder der aktiven Gruppe zurück (unabhängig vom Status)."""
        try:
            active_group = StatusService.get_active_group()
            if not active_group:
                return []

            return db.execute(
                "SELECT b.id, b.benutzername, b.vorname, b.nachname, b.status, b.ist_aktiv "
                "FROM benutzer b "
                "JOIN benutzer_gruppen bg ON b.id = bg.benutzer_id "
                "WHERE bg.gruppen_id = %s "
                "AND b.ist_aktiv = TRUE "
                "ORDER BY b.nachname, b.vorname",
                (active_group["id"],)
            )
        except Exception:
            return []

    @staticmethod
    def get_all_active_users() -> list[dict]:
        """Gibt ALLE aktiven Benutzer zurück (für Fallback-Alarmierung)."""
        try:
            return db.execute(
                "SELECT b.id, b.benutzername, b.vorname, b.nachname, b.status "
                "FROM benutzer b "
                "WHERE b.ist_aktiv = TRUE "
                "ORDER BY b.nachname, b.vorname"
            )
        except Exception:
            return []

    @staticmethod
    def count_available_sanitaeter() -> int:
        """Zählt die verfügbaren Sanitäter der aktiven Gruppe."""
        return len(StatusService.get_available_sanitaeter())

    @staticmethod
    def count_group_members() -> int:
        """Zählt alle Mitglieder der aktiven Gruppe."""
        return len(StatusService.get_all_group_members())
