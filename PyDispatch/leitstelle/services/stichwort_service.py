"""
PyDispatch Leitstelle – Stichwort-Service.
Liest Stichwörter und Standorte aus der Datenbank.
"""

from leitstelle.database.connection import db


class StichwortService:
    """Service für Stichwort-Abfragen."""

    @staticmethod
    def get_all_active_stichwoerter() -> list[dict]:
        """Gibt alle aktiven Stichwörter mit Standort-Info zurück."""
        try:
            results = db.execute(
                "SELECT sw.id, sw.kuerzel, sw.bezeichnung, sw.standort_typ, "
                "sw.fester_standort_id, sw.prioritaet, sw.kategorie, "
                "s.name AS fester_standort_name "
                "FROM stichwoerter sw "
                "LEFT JOIN standorte s ON sw.fester_standort_id = s.id "
                "WHERE sw.ist_aktiv = TRUE "
                "ORDER BY sw.prioritaet DESC, sw.kuerzel"
            )
            return results
        except Exception:
            return []

    @staticmethod
    def get_stichwort_by_id(sw_id: int) -> dict | None:
        """Gibt ein Stichwort anhand der ID zurück."""
        try:
            results = db.execute(
                "SELECT sw.id, sw.kuerzel, sw.bezeichnung, sw.standort_typ, "
                "sw.fester_standort_id, sw.prioritaet, sw.kategorie, "
                "s.name AS fester_standort_name "
                "FROM stichwoerter sw "
                "LEFT JOIN standorte s ON sw.fester_standort_id = s.id "
                "WHERE sw.id = %s",
                (sw_id,)
            )
            return results[0] if results else None
        except Exception:
            return None

    @staticmethod
    def get_auswaehlbare_standorte(stichwort_id: int) -> list[dict]:
        """Gibt die auswählbaren Standorte eines Stichworts zurück."""
        try:
            return db.execute(
                "SELECT s.id, s.name, s.beschreibung "
                "FROM stichwort_standorte ss "
                "JOIN standorte s ON ss.standort_id = s.id "
                "WHERE ss.stichwort_id = %s "
                "AND s.ist_aktiv = TRUE "
                "ORDER BY s.name",
                (stichwort_id,)
            )
        except Exception:
            return []

    @staticmethod
    def get_all_active_standorte() -> list[dict]:
        """Gibt alle aktiven Standorte zurück."""
        try:
            return db.execute(
                "SELECT id, name, beschreibung "
                "FROM standorte WHERE ist_aktiv = TRUE "
                "ORDER BY name"
            )
        except Exception:
            return []
