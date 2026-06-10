import db
import bcrypt

def login(username: str, password: str) -> bool:
    row = db.query("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    if not row:
        return False
    if bcrypt.checkpw(password.encode(), row.password_hash.encode()):
        session["user_id"] = row.id
        return True
    return False

def reset_password(user_id: int, new_password: str) -> None:
    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))

def delete_user(user_id: int, requesting_user_id: int) -> bool:
    admin = db.query("SELECT is_admin FROM users WHERE id = ?", (requesting_user_id,))
    if not admin or not admin.is_admin:
        return False
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return True
