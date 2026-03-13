"""
PyDispatch Admin – Datenbank-Schema und Migrationen.
Erstellt alle benötigten Tabellen in der MySQL-Datenbank.
"""

from admin.database.connection import db

# SQL-Statements für die Tabellen-Erstellung
SCHEMA_SQL = [
    # Einrichtungs-Tabelle
    """
    CREATE TABLE IF NOT EXISTS einrichtung (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        aktualisiert_am DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Benutzergruppen
    """
    CREATE TABLE IF NOT EXISTS benutzergruppen (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        beschreibung TEXT,
        ist_aktiv BOOLEAN DEFAULT TRUE,
        erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        aktualisiert_am DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Benutzer
    """
    CREATE TABLE IF NOT EXISTS benutzer (
        id INT AUTO_INCREMENT PRIMARY KEY,
        benutzername VARCHAR(100) NOT NULL UNIQUE,
        passwort_hash VARCHAR(255) NOT NULL,
        vorname VARCHAR(100),
        nachname VARCHAR(100),
        rolle ENUM('superadmin', 'admin', 'benutzer') DEFAULT 'benutzer',
        ist_aktiv BOOLEAN DEFAULT TRUE,
        status ENUM('in_der_schule', 'nicht_in_der_schule', 'klassenarbeit') DEFAULT 'nicht_in_der_schule',
        erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        aktualisiert_am DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Benutzer-Gruppen-Zuordnung (m:n)
    """
    CREATE TABLE IF NOT EXISTS benutzer_gruppen (
        benutzer_id INT NOT NULL,
        gruppen_id INT NOT NULL,
        PRIMARY KEY (benutzer_id, gruppen_id),
        FOREIGN KEY (benutzer_id) REFERENCES benutzer(id) ON DELETE CASCADE,
        FOREIGN KEY (gruppen_id) REFERENCES benutzergruppen(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Leitstellen-PCs
    """
    CREATE TABLE IF NOT EXISTS leitstellen (
        id INT AUTO_INCREMENT PRIMARY KEY,
        leitstellen_id VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(255) NOT NULL,
        ist_aktiv BOOLEAN DEFAULT TRUE,
        letzter_kontakt DATETIME,
        erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        aktualisiert_am DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Mobile Geräte
    """
    CREATE TABLE IF NOT EXISTS mobile_geraete (
        id INT AUTO_INCREMENT PRIMARY KEY,
        geraete_id VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(255),
        benutzer_id INT,
        ist_aktiv BOOLEAN DEFAULT TRUE,
        letzter_kontakt DATETIME,
        erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        aktualisiert_am DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (benutzer_id) REFERENCES benutzer(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Standorte
    """
    CREATE TABLE IF NOT EXISTS standorte (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        beschreibung TEXT,
        ist_aktiv BOOLEAN DEFAULT TRUE,
        erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Stichwörter
    """
    CREATE TABLE IF NOT EXISTS stichwoerter (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kuerzel VARCHAR(20) NOT NULL,
        bezeichnung VARCHAR(255) NOT NULL,
        standort_typ ENUM('fest', 'auswaehlbar', 'frei') NOT NULL DEFAULT 'frei',
        fester_standort_id INT,
        prioritaet INT DEFAULT 0,
        kategorie VARCHAR(100),
        ist_aktiv BOOLEAN DEFAULT TRUE,
        erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        aktualisiert_am DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (fester_standort_id) REFERENCES standorte(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Stichwort-Standort-Zuordnung (für auswählbare Standorte)
    """
    CREATE TABLE IF NOT EXISTS stichwort_standorte (
        stichwort_id INT NOT NULL,
        standort_id INT NOT NULL,
        PRIMARY KEY (stichwort_id, standort_id),
        FOREIGN KEY (stichwort_id) REFERENCES stichwoerter(id) ON DELETE CASCADE,
        FOREIGN KEY (standort_id) REFERENCES standorte(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Einsätze / Alarme
    """
    CREATE TABLE IF NOT EXISTS einsaetze (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stichwort_id INT NOT NULL,
        standort_text VARCHAR(255),
        standort_id INT,
        leitstelle_id INT,
        alarmiert_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        beendet_am DATETIME,
        status ENUM('aktiv', 'beendet', 'abgebrochen') DEFAULT 'aktiv',
        notiz TEXT,
        FOREIGN KEY (stichwort_id) REFERENCES stichwoerter(id),
        FOREIGN KEY (standort_id) REFERENCES standorte(id),
        FOREIGN KEY (leitstelle_id) REFERENCES leitstellen(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # Aktive Benutzergruppe (welche Gruppe hat aktuell Dienst)
    """
    CREATE TABLE IF NOT EXISTS aktive_gruppe (
        id INT PRIMARY KEY DEFAULT 1,
        gruppen_id INT,
        gesetzt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (gruppen_id) REFERENCES benutzergruppen(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
]


def initialize_database() -> tuple[bool, str]:
    """Erstellt alle Tabellen in der Datenbank."""
    try:
        cursor = db.get_cursor(dictionary=False)
        for sql in SCHEMA_SQL:
            cursor.execute(sql)
        db.connection.commit()
        cursor.close()
        return True, "Datenbank erfolgreich initialisiert."
    except Exception as e:
        return False, f"Fehler bei der Datenbankinitialisierung: {e}"


def check_tables_exist() -> bool:
    """Prüft, ob die Haupttabellen bereits existieren."""
    try:
        results = db.execute("SHOW TABLES")
        table_names = [list(row.values())[0] for row in results]
        required = ["einrichtung", "benutzer", "benutzergruppen", "stichwoerter"]
        return all(t in table_names for t in required)
    except Exception:
        return False
