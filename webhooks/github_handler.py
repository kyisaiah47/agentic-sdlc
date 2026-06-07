"""
GitHub webhook receiver.
Listens for pull_request events and triggers the UiPath Maestro BPMN process.
"""

import os
import json
import hmac
import hashlib
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
UIPATH_WEBHOOK_URL = os.environ["UIPATH_BPMN_TRIGGER_URL"]
UIPATH_API_KEY = os.environ["UIPATH_API_KEY"]


def verify_signature(payload: bytes, signature: str) -> bool:
    if not GITHUB_WEBHOOK_SECRET:
        return True
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def fetch_pr_diff(repo_full_name: str, pr_number: int, token: str) -> str:
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.diff"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text


def trigger_bpmn(payload: dict):
    headers = {
        "Authorization": f"Bearer {UIPATH_API_KEY}",
        "Content-Type": "application/json",
    }
    r = requests.post(UIPATH_WEBHOOK_URL, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        sig = self.headers.get("X-Hub-Signature-256", "")

        if not verify_signature(body, sig):
            self.send_response(401)
            self.end_headers()
            return

        event = self.headers.get("X-GitHub-Event", "")
        if event != "pull_request":
            self.send_response(200)
            self.end_headers()
            return

        data = json.loads(body)
        action = data.get("action", "")

        if action not in ("opened", "synchronize", "reopened"):
            self.send_response(200)
            self.end_headers()
            return

        pr = data["pull_request"]
        repo = data["repository"]

        github_token = os.environ["GITHUB_TOKEN"]
        diff = fetch_pr_diff(repo["full_name"], pr["number"], github_token)

        bpmn_payload = {
            "pr_number": pr["number"],
            "pr_title": pr["title"],
            "pr_description": pr.get("body", ""),
            "pr_url": pr["html_url"],
            "repo": repo["full_name"],
            "branch": pr["head"]["ref"],
            "sha": pr["head"]["sha"],
            "author": pr["user"]["login"],
            "diff": diff,
        }

        result = trigger_bpmn(bpmn_payload)
        print(f"[webhook] triggered BPMN for PR #{pr['number']}: {result}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "triggered"}).encode())

    def log_message(self, format, *args):
        print(f"[webhook] {format % args}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"[webhook] listening on port {port}")
    server.serve_forever()
