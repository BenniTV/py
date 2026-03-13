"""
PyDispatch Admin – Authentifizierungs-Service.
Login-Logik und Session-Verwaltung.
"""

from admin.database.connection import db
from admin.utils.crypto import verify_password


class AuthService:
    """Service für Authentifizierung und Sitzungsverwaltung."""

    _current_user = None

    @classmethod
    def login(cls, benutzername: str, passwort: str) -> tuple[bool, str, dict | None]:
        """Authentifiziert einen Benutzer."""
        try:
            results = db.execute(
                "SELECT id, benutzername, passwort_hash, vorname, nachname, rolle, ist_aktiv "
                "FROM benutzer WHERE benutzername = %s",
                (benutzername,)
            )
            if not results:
                return False, "Benutzername oder Passwort falsch.", None

            user = results[0]
            if not user["ist_aktiv"]:
                return False, "Dieses Konto ist deaktiviert.", None

            if not verify_password(passwort, user["passwort_hash"]):
                return False, "Benutzername oder Passwort falsch.", None

            # Nur Admins und SuperAdmins dürfen sich in der Admin-Software anmelden
            if user["rolle"] not in ("superadmin", "admin"):
                return False, "Keine Berechtigung für die Admin-Software.", None

            cls._current_user = {
                "id": user["id"],
                "benutzername": user["benutzername"],
                "vorname": user["vorname"],
                "nachname": user["nachname"],
                "rolle": user["rolle"],
            }
            return True, "Erfolgreich angemeldet.", cls._current_user

        except Exception as e:
            return False, f"Fehler bei der Anmeldung: {e}", None

    @classmethod
    def logout(cls):
        """Meldet den aktuellen Benutzer ab."""
        cls._current_user = None

    @classmethod
    def get_current_user(cls) -> dict | None:
        """Gibt den aktuell angemeldeten Benutzer zurück."""
        return cls._current_user

    @classmethod
    def is_superadmin(cls) -> bool:
        """Prüft, ob der aktuelle Benutzer SuperAdmin ist."""
        return cls._current_user is not None and cls._current_user.get("rolle") == "superadmin"
