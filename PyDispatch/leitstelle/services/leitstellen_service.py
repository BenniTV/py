"""
PyDispatch Leitstelle – Leitstellen-Service.
Validiert die Leitstellen-ID und verwaltet den Leitstellen-Status.
"""

from leitstelle.database.connection import db


class LeitstellenService:
    """Service für Leitstellen-Operationen."""

    @staticmethod
    def validate_leitstellen_id(ls_id: str) -> tuple[bool, str, dict | None]:
        """Prüft, ob die Leitstellen-ID in der Datenbank existiert und aktiv ist."""
        try:
            results = db.execute(
                "SELECT id, leitstellen_id, name, ist_aktiv "
                "FROM leitstellen WHERE leitstellen_id = %s",
                (ls_id,)
            )
            if not results:
                return False, "Leitstellen-ID nicht gefunden.", None
            ls = results[0]
            if not ls.get("ist_aktiv"):
                return False, "Diese Leitstelle ist deaktiviert.", None
            return True, "Leitstelle validiert.", ls
        except Exception as e:
            return False, f"Fehler bei der Validierung: {e}", None

    @staticmethod
    def update_letzter_kontakt(ls_id: str):
        """Aktualisiert den letzten Kontakt-Zeitstempel."""
        try:
            db.execute_modify(
                "UPDATE leitstellen SET letzter_kontakt = NOW() "
                "WHERE leitstellen_id = %s",
                (ls_id,)
            )
        except Exception:
            pass

    @staticmethod
    def get_einrichtung_name() -> str:
        """Gibt den Einrichtungsnamen aus der Datenbank zurück."""
        try:
            results = db.execute("SELECT name FROM einrichtung LIMIT 1")
            return results[0]["name"] if results else "PyDispatch"
        except Exception:
            return "PyDispatch"
