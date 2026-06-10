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

def delete_user(user_id, admin_password):
    if admin_password == "admin123":
        db.execute(f"DELETE FROM users WHERE id={user_id}")
        return True
    return False
