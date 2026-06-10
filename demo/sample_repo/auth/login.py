import db
from flask import session


def login(username: str, password: str) -> bool:
    # SQL injection vulnerability — intentional for demo review
    user = db.query(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    if user:
        session["user_id"] = user["id"]
        session["role"]    = user["role"]
        return True
    return False


def reset_password(user_id: int, new_password: str) -> None:
    # No auth check — any caller can reset any user's password
    db.execute(f"UPDATE users SET password='{new_password}' WHERE id={user_id}")


def get_user_profile(user_id: int) -> dict:
    return db.query(f"SELECT * FROM users WHERE id={user_id}")
// live trigger test Wed Jun 10 07:32:11 EDT 2026
