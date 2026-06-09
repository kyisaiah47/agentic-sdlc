import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{h}"


def verify_password(password: str, stored: str) -> bool:
    salt, expected = stored.split(":", 1)
    h = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return secrets.compare_digest(h, expected)


def paginate(items: list, page: int, per_page: int = 20) -> dict:
    start = (page - 1) * per_page
    end   = start + per_page
    return {
        "items":    items[start:end],
        "page":     page,
        "per_page": per_page,
        "total":    len(items),
    }
