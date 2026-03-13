"""
PyDispatch Admin – Benutzer-Service.
CRUD-Operationen für Benutzer.
"""

from admin.database.connection import db
from admin.utils.crypto import hash_password


class UserService:
    """Service für Benutzerverwaltung."""

    @staticmethod
    def create_user(benutzername: str, passwort: str, vorname: str = "",
                    nachname: str = "", rolle: str = "benutzer") -> tuple[bool, str, int | None]:
        """Erstellt einen neuen Benutzer."""
        try:
            # Prüfe ob Benutzername bereits existiert
            existing = db.execute(
                "SELECT id FROM benutzer WHERE benutzername = %s", (benutzername,)
            )
            if existing:
                return False, "Benutzername bereits vergeben.", None

            pw_hash = hash_password(passwort)
            user_id = db.execute_insert(
                "INSERT INTO benutzer (benutzername, passwort_hash, vorname, nachname, rolle) "
                "VALUES (%s, %s, %s, %s, %s)",
                (benutzername, pw_hash, vorname, nachname, rolle)
            )
            return True, "Benutzer erfolgreich erstellt.", user_id
        except Exception as e:
            return False, f"Fehler beim Erstellen: {e}", None

    @staticmethod
    def get_all_users() -> list[dict]:
        """Gibt alle Benutzer zurück."""
        try:
            return db.execute(
                "SELECT id, benutzername, vorname, nachname, rolle, ist_aktiv, status, "
                "erstellt_am, aktualisiert_am FROM benutzer ORDER BY benutzername"
            )
        except Exception:
            return []

    @staticmethod
    def get_user_by_id(user_id: int) -> dict | None:
        """Gibt einen Benutzer anhand seiner ID zurück."""
        try:
            results = db.execute(
                "SELECT id, benutzername, vorname, nachname, rolle, ist_aktiv, status "
                "FROM benutzer WHERE id = %s", (user_id,)
            )
            return results[0] if results else None
        except Exception:
            return None

    @staticmethod
    def update_user(user_id: int, vorname: str = None, nachname: str = None,
                    rolle: str = None, ist_aktiv: bool = None) -> tuple[bool, str]:
        """Aktualisiert einen Benutzer."""
        try:
            updates = []
            params = []
            if vorname is not None:
                updates.append("vorname = %s")
                params.append(vorname)
            if nachname is not None:
                updates.append("nachname = %s")
                params.append(nachname)
            if rolle is not None:
                updates.append("rolle = %s")
                params.append(rolle)
            if ist_aktiv is not None:
                updates.append("ist_aktiv = %s")
                params.append(ist_aktiv)

            if not updates:
                return False, "Keine Änderungen angegeben."

            params.append(user_id)
            db.execute_modify(
                f"UPDATE benutzer SET {', '.join(updates)} WHERE id = %s",
                tuple(params)
            )
            return True, "Benutzer aktualisiert."
        except Exception as e:
            return False, f"Fehler beim Aktualisieren: {e}"

    @staticmethod
    def change_password(user_id: int, new_password: str) -> tuple[bool, str]:
        """Ändert das Passwort eines Benutzers."""
        try:
            pw_hash = hash_password(new_password)
            db.execute_modify(
                "UPDATE benutzer SET passwort_hash = %s WHERE id = %s",
                (pw_hash, user_id)
            )
            return True, "Passwort geändert."
        except Exception as e:
            return False, f"Fehler beim Passwort ändern: {e}"

    @staticmethod
    def delete_user(user_id: int) -> tuple[bool, str]:
        """Löscht einen Benutzer."""
        try:
            db.execute_modify("DELETE FROM benutzer WHERE id = %s", (user_id,))
            return True, "Benutzer gelöscht."
        except Exception as e:
            return False, f"Fehler beim Löschen: {e}"

    @staticmethod
    def get_user_groups(user_id: int) -> list[dict]:
        """Gibt die Gruppen eines Benutzers zurück."""
        try:
            return db.execute(
                "SELECT bg.id, bg.name, bg.beschreibung FROM benutzergruppen bg "
                "JOIN benutzer_gruppen bbg ON bg.id = bbg.gruppen_id "
                "WHERE bbg.benutzer_id = %s",
                (user_id,)
            )
        except Exception:
            return []

    @staticmethod
    def assign_groups(user_id: int, group_ids: list[int]) -> tuple[bool, str]:
        """Weist einem Benutzer Gruppen zu (ersetzt alle bisherigen)."""
        try:
            db.execute_modify(
                "DELETE FROM benutzer_gruppen WHERE benutzer_id = %s", (user_id,)
            )
            for gid in group_ids:
                db.execute_insert(
                    "INSERT INTO benutzer_gruppen (benutzer_id, gruppen_id) VALUES (%s, %s)",
                    (user_id, gid)
                )
            return True, "Gruppen zugewiesen."
        except Exception as e:
            return False, f"Fehler bei der Gruppenzuweisung: {e}"

    @staticmethod
    def get_user_count() -> int:
        """Gibt die Gesamtanzahl der Benutzer zurück."""
        try:
            result = db.execute("SELECT COUNT(*) as anzahl FROM benutzer")
            return result[0]["anzahl"] if result else 0
        except Exception:
            return 0
