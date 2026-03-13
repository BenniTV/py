"""
PyDispatch Admin – Eingabevalidierung.
"""

import re


def validate_not_empty(value: str, field_name: str = "Feld") -> tuple[bool, str]:
    """Prüft, ob ein Wert nicht leer ist."""
    if not value or not value.strip():
        return False, f"{field_name} darf nicht leer sein."
    return True, ""


def validate_port(port_str: str) -> tuple[bool, str]:
    """Prüft, ob ein Port gültig ist (1-65535)."""
    try:
        port = int(port_str)
        if 1 <= port <= 65535:
            return True, ""
        return False, "Port muss zwischen 1 und 65535 liegen."
    except ValueError:
        return False, "Port muss eine Zahl sein."


def validate_username(username: str) -> tuple[bool, str]:
    """Prüft, ob ein Benutzername gültig ist."""
    if not username or len(username) < 3:
        return False, "Benutzername muss mindestens 3 Zeichen lang sein."
    if len(username) > 100:
        return False, "Benutzername darf maximal 100 Zeichen lang sein."
    if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
        return False, "Benutzername darf nur Buchstaben, Zahlen, '.', '-' und '_' enthalten."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Prüft, ob ein Passwort den Mindestanforderungen entspricht."""
    if not password or len(password) < 6:
        return False, "Passwort muss mindestens 6 Zeichen lang sein."
    return True, ""
