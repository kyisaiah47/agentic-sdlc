"""
Vercel serverless function — GitHub PR webhook.
Endpoint: POST /api/webhook
"""

import hmac
import hashlib
import json
import os
import requests
from http.server import BaseHTTPRequestHandler


def verify_signature(payload: bytes, signature: str) -> bool:
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    if not secret:
        return True
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def fetch_pr_diff(repo_full_name: str, pr_number: int) -> str:
    token = os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.diff",
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text


def get_uipath_token() -> str:
    r = requests.post(
        "https://staging.uipath.com/identity_/connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["UIPATH_CLIENT_ID"],
            "client_secret": os.environ["UIPATH_CLIENT_SECRET"],
            "scope": "OR.Execution OR.Jobs OR.Jobs.Write OR.Robots.Read OR.Folders.Read OR.Monitoring",
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def trigger_bpmn(payload: dict) -> dict:
    url = os.environ["UIPATH_BPMN_TRIGGER_URL"]
    token = get_uipath_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-UIPATH-OrganizationUnitId": os.environ.get("UIPATH_FOLDER_ID", "3068430"),
    }
    orchestrator_payload = {
        "startInfo": {
            "ReleaseKey": os.environ.get("UIPATH_RELEASE_KEY", "fc25491b-6539-4f6d-9f35-b381fd4789f0"),
            "Strategy": "ModernJobsCount",
            "RobotIds": [],
            "NoOfRobots": 1,
            "Source": "Manual",
            "InputArguments": json.dumps(payload),
        }
    }
    r = requests.post(url, headers=headers, json=orchestrator_payload, timeout=15)
    r.raise_for_status()
    return r.json()


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        sig = self.headers.get("X-Hub-Signature-256", "")

        if not verify_signature(body, sig):
            self._respond(401, {"error": "invalid signature"})
            return

        event = self.headers.get("X-GitHub-Event", "")
        if event != "pull_request":
            self._respond(200, {"status": "ignored", "event": event})
            return

        data = json.loads(body)
        action = data.get("action", "")
        if action not in ("opened", "synchronize", "reopened"):
            self._respond(200, {"status": "ignored", "action": action})
            return

        pr = data["pull_request"]
        repo = data["repository"]

        try:
            diff = fetch_pr_diff(repo["full_name"], pr["number"])
        except Exception as e:
            self._respond(500, {"error": f"failed to fetch diff: {e}"})
            return

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

        try:
            result = trigger_bpmn(bpmn_payload)
            self._respond(200, {"status": "triggered", "bpmn": result})
        except Exception as e:
            self._respond(500, {"error": f"failed to trigger BPMN: {e}"})

    def do_GET(self):
        self._respond(200, {"status": "ok", "service": "uipath-agenthack webhook"})

    def _respond(self, code: int, body: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, format, *args):
        pass
