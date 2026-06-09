"""
Triggers a UiPath Test Cloud test run against a specific branch/SHA.
Called by the Maestro BPMN process after Claude code review passes.

Usage:
  python scripts/trigger_test_run.py --repo owner/repo --branch feature/x --sha abc123
"""

import os
import sys
import time
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

UIPATH_BASE = "https://cloud.uipath.com/{org}/{tenant}"
POLL_INTERVAL = 15  # seconds
MAX_WAIT = 600       # 10 minutes


def get_token(client_id: str, client_secret: str) -> str:
    r = requests.post(
        "https://account.uipath.com/oauth/token",
        json={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "OR.TestSets OR.TestSetExecutions",
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def trigger_run(base_url: str, token: str, test_set_id: str, branch: str, sha: str) -> str:
    url = f"{base_url}/testmanager_/api/v2/testsetexecutions"
    payload = {
        "testSetId": test_set_id,
        "triggerType": "ExternalTool",
        "inputArguments": {"branch": branch, "commitSha": sha},
    }
    r = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["id"]


def poll_run(base_url: str, token: str, execution_id: str) -> dict:
    url = f"{base_url}/testmanager_/api/v2/testsetexecutions/{execution_id}"
    headers = {"Authorization": f"Bearer {token}"}
    elapsed = 0

    while elapsed < MAX_WAIT:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        status = data.get("status", "")

        if status in ("Passed", "Failed", "Faulted", "Aborted"):
            return data

        print(f"[test-cloud] status={status}, waiting...", flush=True)
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    raise TimeoutError(f"Test run {execution_id} did not complete within {MAX_WAIT}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--sha",    required=True)
    parser.add_argument("--test-set-id", default=os.environ.get("UIPATH_TEST_SET_ID"))
    args = parser.parse_args()

    client_id     = os.environ["UIPATH_CLIENT_ID"]
    client_secret = os.environ["UIPATH_CLIENT_SECRET"]
    org           = os.environ["UIPATH_ORG"]
    tenant        = os.environ["UIPATH_TENANT"]

    base_url = UIPATH_BASE.format(org=org, tenant=tenant)

    print(f"[test-cloud] authenticating...", flush=True)
    token = get_token(client_id, client_secret)

    print(f"[test-cloud] triggering test set {args.test_set_id} on {args.branch}@{args.sha[:7]}", flush=True)
    execution_id = trigger_run(base_url, token, args.test_set_id, args.branch, args.sha)
    print(f"[test-cloud] execution_id={execution_id}", flush=True)

    result = poll_run(base_url, token, execution_id)
    status = result["status"]
    passed = status == "Passed"

    summary = {
        "passed": passed,
        "status": status,
        "test_run_id": execution_id,
        "total": result.get("totalTestCases", 0),
        "failed": result.get("failedTestCases", 0),
        "passed_count": result.get("passedTestCases", 0),
    }

    import json
    print(json.dumps(summary, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
