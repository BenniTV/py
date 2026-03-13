"""
PyDispatch Leitstelle – Datenbank-Verbindungsverwaltung.
Verwaltet die MySQL-Verbindung als Singleton.
"""

import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    """Singleton-Klasse für die MySQL-Datenbankverbindung."""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self, host: str, port: int, user: str, password: str, database: str) -> bool:
        """Stellt eine Verbindung zur MySQL-Datenbank her."""
        try:
            self._connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                autocommit=False,
                charset="utf8mb4",
                collation="utf8mb4_unicode_ci",
            )
            return True
        except Error as e:
            print(f"[DB] Verbindungsfehler: {e}")
            return False

    def test_connection(self, host: str, port: int, user: str, password: str,
                        database: str = None) -> tuple[bool, str]:
        """Testet die Verbindung ohne sie dauerhaft zu speichern."""
        try:
            kwargs = dict(host=host, port=port, user=user, password=password)
            if database:
                kwargs["database"] = database
            conn = mysql.connector.connect(**kwargs)
            conn.close()
            return True, "Verbindung erfolgreich"
        except Error as e:
            return False, str(e)

    @property
    def connection(self):
        """Gibt die aktive Verbindung zurück."""
        if self._connection and self._connection.is_connected():
            return self._connection
        return None

    def get_cursor(self, dictionary=True):
        """Gibt einen neuen Cursor zurück."""
        if self.connection:
            return self.connection.cursor(dictionary=dictionary)
        raise ConnectionError("Keine aktive Datenbankverbindung.")

    def execute(self, query: str, params: tuple = None) -> list:
        """Führt eine SELECT-Query aus und gibt die Ergebnisse zurück."""
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()

    def execute_modify(self, query: str, params: tuple = None) -> int:
        """Führt eine INSERT/UPDATE/DELETE-Query aus."""
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params)
            self._connection.commit()
            return cursor.rowcount
        except Error:
            self._connection.rollback()
            raise
        finally:
            cursor.close()

    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Führt ein INSERT aus und gibt die lastrowid zurück."""
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params)
            self._connection.commit()
            return cursor.lastrowid
        except Error:
            self._connection.rollback()
            raise
        finally:
            cursor.close()

    def disconnect(self):
        """Trennt die Datenbankverbindung."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def is_connected(self) -> bool:
        """Prüft, ob eine aktive Verbindung besteht."""
        return self._connection is not None and self._connection.is_connected()


# Globale Instanz
db = DatabaseConnection()
