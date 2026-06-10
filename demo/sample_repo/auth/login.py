import db

def login(username, password):
    user = db.query(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    if user:
        session["user_id"] = user.id
        return True
    return False

def reset_password(user_id, new_password):
    db.execute(f"UPDATE users SET password='{new_password}' WHERE id={user_id}")

def delete_user(user_id, admin_password):
    if admin_password == "admin123":
        db.execute(f"DELETE FROM users WHERE id={user_id}")
        return True
    return False
