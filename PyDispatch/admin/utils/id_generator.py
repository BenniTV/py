"""
PyDispatch Admin – ID-Generator.
Erzeugt eindeutige IDs für Leitstellen und Mobile Geräte.
"""

import secrets
import string


def generate_leitstellen_id() -> str:
    """Generiert eine eindeutige Leitstellen-ID (LS-XXXXXXXX)."""
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(secrets.choice(chars) for _ in range(8))
    return f"LS-{random_part}"


def generate_geraete_id() -> str:
    """Generiert eine eindeutige Geräte-ID (MG-XXXXXXXX)."""
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(secrets.choice(chars) for _ in range(8))
    return f"MG-{random_part}"
