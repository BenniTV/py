"""
PyDispatch Admin – Gruppen-Service.
CRUD-Operationen für Benutzergruppen.
"""

from admin.database.connection import db


class GroupService:
    """Service für die Verwaltung von Benutzergruppen."""

    @staticmethod
    def create_group(name: str, beschreibung: str = "") -> tuple[bool, str, int | None]:
        """Erstellt eine neue Benutzergruppe."""
        try:
            existing = db.execute(
                "SELECT id FROM benutzergruppen WHERE name = %s", (name,)
            )
            if existing:
                return False, "Gruppenname bereits vergeben.", None

            group_id = db.execute_insert(
                "INSERT INTO benutzergruppen (name, beschreibung) VALUES (%s, %s)",
                (name, beschreibung)
            )
            return True, "Gruppe erfolgreich erstellt.", group_id
        except Exception as e:
            return False, f"Fehler beim Erstellen: {e}", None

    @staticmethod
    def get_all_groups() -> list[dict]:
        """Gibt alle Benutzergruppen zurück."""
        try:
            return db.execute(
                "SELECT bg.id, bg.name, bg.beschreibung, bg.ist_aktiv, bg.erstellt_am, "
                "(SELECT COUNT(*) FROM benutzer_gruppen bbg WHERE bbg.gruppen_id = bg.id) as mitglieder_anzahl "
                "FROM benutzergruppen bg ORDER BY bg.name"
            )
        except Exception:
            return []

    @staticmethod
    def get_group_by_id(group_id: int) -> dict | None:
        """Gibt eine Gruppe anhand ihrer ID zurück."""
        try:
            results = db.execute(
                "SELECT id, name, beschreibung, ist_aktiv FROM benutzergruppen WHERE id = %s",
                (group_id,)
            )
            return results[0] if results else None
        except Exception:
            return None

    @staticmethod
    def update_group(group_id: int, name: str = None, beschreibung: str = None,
                     ist_aktiv: bool = None) -> tuple[bool, str]:
        """Aktualisiert eine Benutzergruppe."""
        try:
            updates = []
            params = []
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if beschreibung is not None:
                updates.append("beschreibung = %s")
                params.append(beschreibung)
            if ist_aktiv is not None:
                updates.append("ist_aktiv = %s")
                params.append(ist_aktiv)

            if not updates:
                return False, "Keine Änderungen angegeben."

            params.append(group_id)
            db.execute_modify(
                f"UPDATE benutzergruppen SET {', '.join(updates)} WHERE id = %s",
                tuple(params)
            )
            return True, "Gruppe aktualisiert."
        except Exception as e:
            return False, f"Fehler beim Aktualisieren: {e}"

    @staticmethod
    def delete_group(group_id: int) -> tuple[bool, str]:
        """Löscht eine Benutzergruppe."""
        try:
            db.execute_modify("DELETE FROM benutzergruppen WHERE id = %s", (group_id,))
            return True, "Gruppe gelöscht."
        except Exception as e:
            return False, f"Fehler beim Löschen: {e}"

    @staticmethod
    def get_group_members(group_id: int) -> list[dict]:
        """Gibt alle Mitglieder einer Gruppe zurück."""
        try:
            return db.execute(
                "SELECT b.id, b.benutzername, b.vorname, b.nachname, b.rolle, b.ist_aktiv, b.status "
                "FROM benutzer b "
                "JOIN benutzer_gruppen bg ON b.id = bg.benutzer_id "
                "WHERE bg.gruppen_id = %s ORDER BY b.nachname, b.vorname",
                (group_id,)
            )
        except Exception:
            return []

    @staticmethod
    def get_group_count() -> int:
        """Gibt die Gesamtanzahl der Gruppen zurück."""
        try:
            result = db.execute("SELECT COUNT(*) as anzahl FROM benutzergruppen")
            return result[0]["anzahl"] if result else 0
        except Exception:
            return 0

    @staticmethod
    def set_active_group(group_id: int) -> tuple[bool, str]:
        """Setzt die aktuell aktive Benutzergruppe."""
        try:
            # Upsert: aktive Gruppe setzen oder aktualisieren
            db.execute_modify(
                "INSERT INTO aktive_gruppe (id, gruppen_id) VALUES (1, %s) "
                "ON DUPLICATE KEY UPDATE gruppen_id = %s, gesetzt_am = CURRENT_TIMESTAMP",
                (group_id, group_id)
            )
            return True, "Aktive Gruppe gesetzt."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def get_active_group() -> dict | None:
        """Gibt die aktuell aktive Gruppe zurück."""
        try:
            results = db.execute(
                "SELECT bg.id, bg.name FROM aktive_gruppe ag "
                "JOIN benutzergruppen bg ON ag.gruppen_id = bg.id WHERE ag.id = 1"
            )
            return results[0] if results else None
        except Exception:
            return None
