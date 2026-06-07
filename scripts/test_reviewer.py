import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from agents.claude_reviewer import review_pr

SAMPLE_DIFF = """
diff --git a/auth/login.py b/auth/login.py
index 3f2a1b..8c4d9e 100644
--- a/auth/login.py
+++ b/auth/login.py
@@ -12,8 +12,14 @@ import db
 def login(username, password):
-    user = db.query(f"SELECT * FROM users WHERE username='{username}'")
-    if user and user.password == password:
+    user = db.query(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
+    if user:
         session["user_id"] = user.id
         return True
     return False
+
+def reset_password(user_id, new_password):
+    db.execute(f"UPDATE users SET password='{new_password}' WHERE id={user_id}")
"""

result = review_pr(
    pr_diff=SAMPLE_DIFF,
    pr_title="Fix login query and add password reset",
    pr_description="Combines username/password check into one query for efficiency. Adds reset_password helper.",
)

print(json.dumps(result, indent=2))
