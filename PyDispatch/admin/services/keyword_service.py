"""
PyDispatch Admin – Stichwort-Service.
CRUD-Operationen für Stichwörter und Standorte.
"""

from admin.database.connection import db


class KeywordService:
    """Service für die Verwaltung von Stichwörtern und Standorten."""

    # ── Standorte ──

    @staticmethod
    def create_standort(name: str, beschreibung: str = "") -> tuple[bool, str, int | None]:
        """Erstellt einen neuen Standort."""
        try:
            sid = db.execute_insert(
                "INSERT INTO standorte (name, beschreibung) VALUES (%s, %s)",
                (name, beschreibung)
            )
            return True, "Standort erstellt.", sid
        except Exception as e:
            return False, f"Fehler: {e}", None

    @staticmethod
    def get_all_standorte() -> list[dict]:
        """Gibt alle Standorte zurück."""
        try:
            return db.execute(
                "SELECT id, name, beschreibung, ist_aktiv, erstellt_am "
                "FROM standorte ORDER BY name"
            )
        except Exception:
            return []

    @staticmethod
    def update_standort(standort_id: int, name: str = None,
                        beschreibung: str = None, ist_aktiv: bool = None) -> tuple[bool, str]:
        """Aktualisiert einen Standort."""
        try:
            updates, params = [], []
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
                return False, "Keine Änderungen."
            params.append(standort_id)
            db.execute_modify(
                f"UPDATE standorte SET {', '.join(updates)} WHERE id = %s", tuple(params)
            )
            return True, "Standort aktualisiert."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def delete_standort(standort_id: int) -> tuple[bool, str]:
        """Löscht einen Standort."""
        try:
            db.execute_modify("DELETE FROM standorte WHERE id = %s", (standort_id,))
            return True, "Standort gelöscht."
        except Exception as e:
            return False, f"Fehler: {e}"

    # ── Stichwörter ──

    @staticmethod
    def create_stichwort(kuerzel: str, bezeichnung: str, standort_typ: str = "frei",
                         fester_standort_id: int = None, prioritaet: int = 0,
                         kategorie: str = "", standort_ids: list[int] = None) -> tuple[bool, str, int | None]:
        """Erstellt ein neues Stichwort."""
        try:
            sw_id = db.execute_insert(
                "INSERT INTO stichwoerter (kuerzel, bezeichnung, standort_typ, "
                "fester_standort_id, prioritaet, kategorie) VALUES (%s, %s, %s, %s, %s, %s)",
                (kuerzel, bezeichnung, standort_typ, fester_standort_id, prioritaet, kategorie)
            )
            # Bei auswählbaren Standorten: Zuordnungen erstellen
            if standort_typ == "auswaehlbar" and standort_ids:
                for sid in standort_ids:
                    db.execute_insert(
                        "INSERT INTO stichwort_standorte (stichwort_id, standort_id) VALUES (%s, %s)",
                        (sw_id, sid)
                    )
            return True, "Stichwort erstellt.", sw_id
        except Exception as e:
            return False, f"Fehler: {e}", None

    @staticmethod
    def get_all_stichwoerter() -> list[dict]:
        """Gibt alle Stichwörter zurück."""
        try:
            return db.execute(
                "SELECT sw.id, sw.kuerzel, sw.bezeichnung, sw.standort_typ, "
                "sw.fester_standort_id, sw.prioritaet, sw.kategorie, sw.ist_aktiv, "
                "sw.erstellt_am, s.name as fester_standort_name "
                "FROM stichwoerter sw "
                "LEFT JOIN standorte s ON sw.fester_standort_id = s.id "
                "ORDER BY sw.prioritaet DESC, sw.kuerzel"
            )
        except Exception:
            return []

    @staticmethod
    def get_stichwort_by_id(sw_id: int) -> dict | None:
        """Gibt ein Stichwort anhand seiner ID zurück."""
        try:
            results = db.execute(
                "SELECT id, kuerzel, bezeichnung, standort_typ, fester_standort_id, "
                "prioritaet, kategorie, ist_aktiv FROM stichwoerter WHERE id = %s",
                (sw_id,)
            )
            return results[0] if results else None
        except Exception:
            return None

    @staticmethod
    def get_stichwort_standorte(sw_id: int) -> list[dict]:
        """Gibt die auswählbaren Standorte eines Stichworts zurück."""
        try:
            return db.execute(
                "SELECT s.id, s.name FROM standorte s "
                "JOIN stichwort_standorte ss ON s.id = ss.standort_id "
                "WHERE ss.stichwort_id = %s ORDER BY s.name",
                (sw_id,)
            )
        except Exception:
            return []

    @staticmethod
    def update_stichwort(sw_id: int, kuerzel: str = None, bezeichnung: str = None,
                         standort_typ: str = None, fester_standort_id: int = None,
                         prioritaet: int = None, kategorie: str = None,
                         ist_aktiv: bool = None, standort_ids: list[int] = None) -> tuple[bool, str]:
        """Aktualisiert ein Stichwort."""
        try:
            updates, params = [], []
            if kuerzel is not None:
                updates.append("kuerzel = %s")
                params.append(kuerzel)
            if bezeichnung is not None:
                updates.append("bezeichnung = %s")
                params.append(bezeichnung)
            if standort_typ is not None:
                updates.append("standort_typ = %s")
                params.append(standort_typ)
            if fester_standort_id is not None:
                updates.append("fester_standort_id = %s")
                params.append(fester_standort_id if fester_standort_id > 0 else None)
            if prioritaet is not None:
                updates.append("prioritaet = %s")
                params.append(prioritaet)
            if kategorie is not None:
                updates.append("kategorie = %s")
                params.append(kategorie)
            if ist_aktiv is not None:
                updates.append("ist_aktiv = %s")
                params.append(ist_aktiv)

            if updates:
                params.append(sw_id)
                db.execute_modify(
                    f"UPDATE stichwoerter SET {', '.join(updates)} WHERE id = %s",
                    tuple(params)
                )

            # Standort-Zuordnungen aktualisieren
            if standort_ids is not None:
                db.execute_modify(
                    "DELETE FROM stichwort_standorte WHERE stichwort_id = %s", (sw_id,)
                )
                for sid in standort_ids:
                    db.execute_insert(
                        "INSERT INTO stichwort_standorte (stichwort_id, standort_id) VALUES (%s, %s)",
                        (sw_id, sid)
                    )

            return True, "Stichwort aktualisiert."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def delete_stichwort(sw_id: int) -> tuple[bool, str]:
        """Löscht ein Stichwort."""
        try:
            db.execute_modify("DELETE FROM stichwoerter WHERE id = %s", (sw_id,))
            return True, "Stichwort gelöscht."
        except Exception as e:
            return False, f"Fehler: {e}"

    @staticmethod
    def get_stichwort_count() -> int:
        """Gibt die Anzahl der Stichwörter zurück."""
        try:
            result = db.execute("SELECT COUNT(*) as anzahl FROM stichwoerter")
            return result[0]["anzahl"] if result else 0
        except Exception:
            return 0

    @staticmethod
    def get_einsatz_count() -> int:
        """Gibt die Anzahl der registrierten Einsätze zurück."""
        try:
            result = db.execute("SELECT COUNT(*) as anzahl FROM einsaetze")
            return result[0]["anzahl"] if result else 0
        except Exception:
            return 0
