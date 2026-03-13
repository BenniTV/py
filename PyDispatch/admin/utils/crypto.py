"""
PyDispatch Admin – Kryptographie-Utilities.
Passwort-Hashing und -Verifizierung mit SHA-256 + Salt.
"""

import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hasht ein Passwort mit SHA-256 und zufälligem Salt."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{pw_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifiziert ein Passwort gegen den gespeicherten Hash."""
    try:
        salt, pw_hash = stored_hash.split(":", 1)
        check_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return secrets.compare_digest(check_hash, pw_hash)
    except (ValueError, AttributeError):
        return False
