"""
Triggers a production deployment via GitHub Actions workflow_dispatch.
Called by the Maestro BPMN process after human approval.

Usage:
  python scripts/deploy.py --repo owner/repo --ref main --sha abc123 --deploy-id deploy-42
"""

import os
import sys
import time
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"
WORKFLOW_FILE = "deploy.yml"
POLL_INTERVAL = 20
MAX_WAIT = 600


def dispatch_workflow(repo: str, ref: str, sha: str, deploy_id: str, token: str) -> None:
    url = f"{GITHUB_API}/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    r = requests.post(
        url,
        json={"ref": ref, "inputs": {"sha": sha, "deploy_id": deploy_id}},
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15,
    )
    r.raise_for_status()


def find_run(repo: str, sha: str, token: str) -> str | None:
    """Return the run ID for the deploy workflow triggered by this SHA, or None."""
    url = f"{GITHUB_API}/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/runs"
    r = requests.get(
        url,
        params={"head_sha": sha, "per_page": 5},
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15,
    )
    r.raise_for_status()
    runs = r.json().get("workflow_runs", [])
    return runs[0]["id"] if runs else None


def poll_run(repo: str, run_id: str, token: str) -> dict:
    url = f"{GITHUB_API}/repos/{repo}/actions/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    elapsed = 0

    while elapsed < MAX_WAIT:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()

        status     = data.get("status", "")
        conclusion = data.get("conclusion")

        if status == "completed":
            return {"success": conclusion == "success", "conclusion": conclusion, "run_id": run_id, "url": data["html_url"]}

        print(f"[deploy] status={status}, waiting...", flush=True)
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    raise TimeoutError(f"Deploy run {run_id} did not complete within {MAX_WAIT}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo",      required=True, help="owner/repo")
    parser.add_argument("--ref",       default="main", help="branch/tag to deploy")
    parser.add_argument("--sha",       required=True)
    parser.add_argument("--deploy-id", required=True)
    args = parser.parse_args()

    token = os.environ["GITHUB_TOKEN"]

    print(f"[deploy] dispatching workflow for {args.repo}@{args.sha[:7]}", flush=True)
    dispatch_workflow(args.repo, args.ref, args.sha, args.deploy_id, token)

    # Give GitHub a few seconds to register the run
    time.sleep(5)

    # Locate the triggered run
    run_id = None
    for _ in range(10):
        run_id = find_run(args.repo, args.sha, token)
        if run_id:
            break
        time.sleep(3)

    if not run_id:
        print("[deploy] ERROR: could not find workflow run after dispatch", file=sys.stderr)
        sys.exit(1)

    print(f"[deploy] run_id={run_id}", flush=True)
    result = poll_run(args.repo, run_id, token)

    import json
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
