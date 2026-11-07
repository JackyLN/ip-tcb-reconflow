"""HTTP-only Docker smoke using private seed stdout; never prints credentials."""

import argparse
import re
import time
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://localhost:8080")
parser.add_argument("--credentials", default="artifacts/demo-credentials.txt")
args = parser.parse_args()
credentials = {}
for line in Path(args.credentials).read_text().splitlines():
    match = re.match(r"(\w+@reconflow\.demo)\s+(\S+)$", line)
    if match:
        credentials[match[1]] = match[2]


def csrf(client: httpx.Client, path: str = "/") -> str:
    response = client.get(path)
    response.raise_for_status()
    return re.search(r'name="csrf_value" value="([^"]+)"', response.text).group(1)


def signin(client: httpx.Client, role: str) -> str:
    email = f"{role}@reconflow.demo"
    response = client.post(
        "/login",
        data={"csrf_value": csrf(client, "/login"), "email": email, "password": credentials[email]},
    )
    response.raise_for_status()
    assert response.url.path == "/", "Sign-in failed"
    return csrf(client)


def wait_for(client: httpx.Client, path: str, text: str) -> str:
    for _ in range(40):
        response = client.get(path)
        response.raise_for_status()
        if text in response.text:
            return response.text
        time.sleep(0.5)
    raise AssertionError(f"Timed out waiting for {text} at {path}")


with httpx.Client(base_url=args.url, follow_redirects=True, timeout=30) as client:
    assert client.get("/healthz").json()["status"] == "ok"
    assert client.get("/readyz").json()["status"] == "ready"
    token = signin(client, "analyst")
    response = client.post(
        "/scenarios", data={"csrf_value": token, "scenario": "mismatch", "count": 1000}
    )
    response.raise_for_status()
    import_path = response.url.path
    page = wait_for(client, import_path, "COMPLETED")
    run_id = re.search(r'href="/runs/(\d+)"', page).group(1)
    assert "AMBIGUOUS" in client.get(f"/runs/{run_id}").text
    replay = client.post(import_path + "/replay", data={"csrf_value": token})
    assert replay.url.path == import_path
    page = client.get("/exceptions").text
    ids = re.findall(r'href="/exceptions/(\d+)"', page)
    case_id = next(
        i for i in ids if '<span class="badge">OPEN</span>' in client.get(f"/exceptions/{i}").text
    )
    path = f"/exceptions/{case_id}"
    client.post(path + "/investigate", data={"csrf_value": token}).raise_for_status()
    wait_for(client, path, "SIMULATED")
    client.post(
        path + "/propose",
        data={
            "csrf_value": token,
            "note": "Synthetic smoke: evidence checked; recommend supervised closure.",
        },
    ).raise_for_status()
    token = signin(client, "supervisor")
    page = client.get("/review").text
    proposal_id = re.search(r'action="/review/(\d+)"', page).group(1)
    client.post(
        f"/review/{proposal_id}", data={"csrf_value": token, "decision": "APPROVED"}
    ).raise_for_status()
    assert "RESOLVED" in client.get(path).text
    token = signin(client, "admin")
    client.post("/controls/ai", data={"csrf_value": token, "enabled": "false"}).raise_for_status()
    assert "DISABLED" in client.get("/controls").text
    client.post("/controls/ai", data={"csrf_value": token, "enabled": "true"}).raise_for_status()
    response = client.post(
        "/scenarios", data={"csrf_value": token, "scenario": "failure", "count": 100}
    )
    response.raise_for_status()
    wait_for(client, response.url.path, "COMPLETED")
    assert "job.failed" in client.get("/audit").text
    for path in (
        "/",
        "/imports",
        "/runs",
        "/payouts",
        "/exceptions",
        "/investigations",
        "/review",
        "/reports/operations",
        "/reports/impact",
        "/ai/evaluation",
        "/audit",
        "/controls",
        "/operations/health",
        "/guide",
    ):
        client.get(path).raise_for_status()
print(
    "PASS: PostgreSQL HTTP login, 1,000-payment reconciliation, replay, simulated AI, "
    "independent approval, kill switch, failure/retry and 14 screens"
)
