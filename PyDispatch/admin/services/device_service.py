"""
PyDispatch Admin – Geräte-Service.
CRUD-Operationen für Leitstellen-PCs und mobile Geräte.
"""

from admin.database.connection import db
from admin.utils.id_generator import generate_leitstellen_id, generate_geraete_id


class DeviceService:
    """Service für die Verwaltung von Geräten."""

    # ── Leitstellen ──

    @staticmethod
    def create_leitstelle(name: str) -> tuple[bool, str, str | None]:
        """Erstellt eine neue Leitstelle und gibt die generierte ID zurück."""
        try:
            ls_id = generate_leitstellen_id()
            # Stelle sicher, dass die ID einzigartig ist
            while db.execute("SELECT id FROM leitstellen WHERE leitstellen_id = %s", (ls_id,)):
                ls_id = generate_leitstellen_id()

            db.execute_insert(
                "INSERT INTO leitstellen (leitstellen_id, name) VALUES (%s, %s)",
                (ls_id, name)
            )
            return True, f"Leitstelle erstellt. ID: {ls_id}", ls_id
        except Exception as e:
            return False, f"Fehler: {e}", None

    @staticmethod
    def get_all_leitstellen() -> list[dict]:
        """Gibt alle Leitstellen zurück."""
        try:
            return db.execute(
                "SELECT id, leitstellen_id, name, ist_aktiv, letzter_kontakt, erstellt_am "
                "FROM leitstellen ORDER BY name"
            )
        except Exception:
            return []

    @staticmethod
    def update_leitstelle(ls_db_id: int, name: str = None, ist_aktiv: bool = None) -> tuple[bool, str]:
        """Aktualisiert eine Leitstelle."""
        try:
            updates, params = [], []
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if ist_aktiv is not None:
                updates.append("ist_aktiv = %s")
                params.append(ist_aktiv)
            if not updates:
                return False, "Keine Änderungen."
            params.append(ls_db_id)
            db.execute_modify(
                f"UPDATE leitstellen SET {', '.join(updates)} WHERE id = %s", tuple(params)
            )
            return True, "Leitstelle aktualisiert."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def delete_leitstelle(ls_db_id: int) -> tuple[bool, str]:
        """Löscht eine Leitstelle."""
        try:
            db.execute_modify("DELETE FROM leitstellen WHERE id = %s", (ls_db_id,))
            return True, "Leitstelle gelöscht."
        except Exception as e:
            return False, f"Fehler: {e}"

    # ── Mobile Geräte ──

    @staticmethod
    def create_mobile_device(name: str, benutzer_id: int = None) -> tuple[bool, str, str | None]:
        """Erstellt ein neues mobiles Gerät und gibt die generierte ID zurück."""
        try:
            mg_id = generate_geraete_id()
            while db.execute("SELECT id FROM mobile_geraete WHERE geraete_id = %s", (mg_id,)):
                mg_id = generate_geraete_id()

            db.execute_insert(
                "INSERT INTO mobile_geraete (geraete_id, name, benutzer_id) VALUES (%s, %s, %s)",
                (mg_id, name, benutzer_id)
            )
            return True, f"Gerät erstellt. ID: {mg_id}", mg_id
        except Exception as e:
            return False, f"Fehler: {e}", None

    @staticmethod
    def get_all_mobile_devices() -> list[dict]:
        """Gibt alle mobilen Geräte zurück."""
        try:
            return db.execute(
                "SELECT mg.id, mg.geraete_id, mg.name, mg.ist_aktiv, mg.letzter_kontakt, "
                "mg.erstellt_am, b.benutzername, b.vorname, b.nachname "
                "FROM mobile_geraete mg "
                "LEFT JOIN benutzer b ON mg.benutzer_id = b.id "
                "ORDER BY mg.name"
            )
        except Exception:
            return []

    @staticmethod
    def update_mobile_device(device_db_id: int, name: str = None,
                             benutzer_id: int = None, ist_aktiv: bool = None) -> tuple[bool, str]:
        """Aktualisiert ein mobiles Gerät."""
        try:
            updates, params = [], []
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if benutzer_id is not None:
                updates.append("benutzer_id = %s")
                params.append(benutzer_id if benutzer_id > 0 else None)
            if ist_aktiv is not None:
                updates.append("ist_aktiv = %s")
                params.append(ist_aktiv)
            if not updates:
                return False, "Keine Änderungen."
            params.append(device_db_id)
            db.execute_modify(
                f"UPDATE mobile_geraete SET {', '.join(updates)} WHERE id = %s", tuple(params)
            )
            return True, "Gerät aktualisiert."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def delete_mobile_device(device_db_id: int) -> tuple[bool, str]:
        """Löscht ein mobiles Gerät."""
        try:
            db.execute_modify("DELETE FROM mobile_geraete WHERE id = %s", (device_db_id,))
            return True, "Gerät gelöscht."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def get_leitstellen_count() -> int:
        """Gibt die Anzahl der Leitstellen zurück."""
        try:
            result = db.execute("SELECT COUNT(*) as anzahl FROM leitstellen")
            return result[0]["anzahl"] if result else 0
        except Exception:
            return 0

    @staticmethod
    def get_mobile_device_count() -> int:
        """Gibt die Anzahl der mobilen Geräte zurück."""
        try:
            result = db.execute("SELECT COUNT(*) as anzahl FROM mobile_geraete")
            return result[0]["anzahl"] if result else 0
        except Exception:
            return 0
