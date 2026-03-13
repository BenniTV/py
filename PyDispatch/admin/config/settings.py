"""
PyDispatch Admin – Lokale Konfigurationsverwaltung.
Speichert ausschließlich die MySQL-Verbindungsdaten lokal (JSON-Datei).
"""

import json
import os
from pathlib import Path

# Konfigurationsdatei im Benutzerverzeichnis
CONFIG_DIR = Path.home() / ".pydispatch"
CONFIG_FILE = CONFIG_DIR / "admin_config.json"

DEFAULT_CONFIG = {
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "",
        "password": "",
        "database": ""
    },
    "einrichtung": {
        "name": ""
    }
}


def ensure_config_dir():
    """Erstellt das Konfigurationsverzeichnis, falls es nicht existiert."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def config_exists() -> bool:
    """Prüft, ob eine lokale Konfiguration vorhanden ist."""
    return CONFIG_FILE.exists()


def load_config() -> dict:
    """Lädt die lokale Konfiguration."""
    if not config_exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Speichert die Konfiguration lokal."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_mysql_config() -> dict:
    """Gibt die MySQL-Verbindungsdaten zurück."""
    config = load_config()
    return config.get("mysql", DEFAULT_CONFIG["mysql"])


def save_mysql_config(host: str, port: int, user: str, password: str, database: str):
    """Speichert die MySQL-Verbindungsdaten."""
    config = load_config()
    config["mysql"] = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database
    }
    save_config(config)


def get_einrichtung_name() -> str:
    """Gibt den Einrichtungsnamen zurück."""
    config = load_config()
    return config.get("einrichtung", {}).get("name", "")


def save_einrichtung_name(name: str):
    """Speichert den Einrichtungsnamen."""
    config = load_config()
    config["einrichtung"] = {"name": name}
    save_config(config)


def delete_config():
    """Löscht die lokale Konfiguration."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
