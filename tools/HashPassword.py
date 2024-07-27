

import hashlib
import hmac

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify if the provided password matches the stored hash."""
    return hmac.compare_digest(hash_password(password), stored_hash)

