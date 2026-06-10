"""
Post-deploy regression monitoring agent.
Polls health endpoints + key metrics after a production deploy.
Signals UiPath BPMN to trigger rollback case if regression detected.
"""

import os
import json
import time
import requests

UIPATH_API_BASE = "https://staging.uipath.com/{org}/{tenant}/orchestrator_"
ROLLBACK_PROCESS = "RollbackBPMN"


def check_health(endpoints: list[str]) -> dict:
    results = {}
    for url in endpoints:
        try:
            r = requests.get(url, timeout=10)
            results[url] = {"status": r.status_code, "ok": r.status_code < 400}
        except Exception as e:
            results[url] = {"status": None, "ok": False, "error": str(e)}
    return results


def trigger_rollback(deploy_id: str, reason: str, token: str, org: str, tenant: str):
    url = f"https://staging.uipath.com/{org}/{tenant}/orchestrator_/api/v1/processes/start"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "processName": ROLLBACK_PROCESS,
        "inputArguments": json.dumps({"deployId": deploy_id, "reason": reason}),
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()


def monitor(config: dict):
    endpoints = config["health_endpoints"]
    deploy_id = config["deploy_id"]
    poll_interval = config.get("poll_interval_seconds", 30)
    max_failures = config.get("max_consecutive_failures", 3)
    token = os.environ["UIPATH_ACCESS_TOKEN"]
    org = os.environ["UIPATH_ORG"]
    tenant = os.environ["UIPATH_TENANT"]

    consecutive_failures = 0

    for _ in range(config.get("max_checks", 20)):
        health = check_health(endpoints)
        failed = [url for url, r in health.items() if not r["ok"]]

        if failed:
            consecutive_failures += 1
            print(f"[monitor] failures={consecutive_failures} endpoints={failed}")
            if consecutive_failures >= max_failures:
                reason = f"Health check failed {consecutive_failures}x: {failed}"
                trigger_rollback(deploy_id, reason, token, org, tenant)
                print(f"[monitor] rollback triggered: {reason}")
                return
        else:
            consecutive_failures = 0
            print(f"[monitor] all healthy")

        time.sleep(poll_interval)

    print("[monitor] monitoring window complete, no regression detected")


if __name__ == "__main__":
    import sys
    config = json.loads(sys.stdin.read())
    monitor(config)
