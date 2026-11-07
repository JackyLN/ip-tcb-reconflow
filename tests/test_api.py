from conftest import sign_in, token
from sqlalchemy import select

from reconflow.db import SessionLocal
from reconflow.models import Case, Proposal
from reconflow.worker import tick

ROUTES = [
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
]


def test_login_csrf_and_main_routes(client):
    assert client.get("/").url.path == "/login"
    assert (
        client.post(
            "/login",
            data={
                "email": "analyst@reconflow.demo",
                "password": "test-password",
                "csrf_value": "bad",
            },
        ).status_code
        == 403
    )
    sign_in(client)
    for path in ROUTES:
        assert client.get(path).status_code == 200, path
    assert client.get("/healthz").json()["status"] == "ok"


def test_end_to_end_dual_control(client):
    csrf = sign_in(client)
    response = client.post(
        "/scenarios", data={"csrf_value": csrf, "scenario": "mismatch", "count": 1000}
    )
    assert response.status_code == 200
    tick()
    with SessionLocal() as db:
        case = db.scalar(select(Case))
        case_id = case.id
    assert client.get(f"/exceptions/{case_id}").status_code == 200
    assert client.get("/payouts/1").status_code == 200
    assert client.get("/runs/1").status_code == 200
    assert (
        client.post(f"/exceptions/{case_id}/investigate", data={"csrf_value": csrf}).status_code
        == 200
    )
    tick()
    assert "SIMULATED" in client.get(f"/exceptions/{case_id}").text
    assert (
        client.post(
            f"/exceptions/{case_id}/propose",
            data={
                "csrf_value": csrf,
                "note": "Provider statement checked; resolve synthetic case.",
            },
        ).status_code
        == 200
    )
    with SessionLocal() as db:
        proposal = db.scalar(select(Proposal))
        pid = proposal.id
    assert (
        client.post(f"/review/{pid}", data={"csrf_value": csrf, "decision": "APPROVED"}).status_code
        == 403
    )
    csrf = sign_in(client, "supervisor")
    assert (
        client.post(f"/review/{pid}", data={"csrf_value": csrf, "decision": "APPROVED"}).status_code
        == 200
    )
    with SessionLocal() as db:
        assert db.get(Case, case_id).status == "RESOLVED"


def test_auditor_cannot_mutate_and_admin_kill(client):
    csrf = sign_in(client, "auditor")
    assert (
        client.post(
            "/scenarios", data={"csrf_value": csrf, "scenario": "clean", "count": 100}
        ).status_code
        == 403
    )
    assert (
        client.post("/controls/ai", data={"csrf_value": csrf, "enabled": "false"}).status_code
        == 403
    )
    csrf = sign_in(client, "admin")
    assert (
        client.post("/controls/ai", data={"csrf_value": csrf, "enabled": "false"}).status_code
        == 200
    )
    assert "DISABLED" in client.get("/controls").text
    assert (
        client.post(
            "/controls/providers",
            data={"csrf_value": csrf, "name": "SecondPay-v1", "fee_bps": 150, "tolerance": 0},
        ).status_code
        == 200
    )


def test_import_validation_and_replay(client):
    csrf = sign_in(client)
    raw = client.get("/imports/template.csv").content
    first = client.post(
        "/imports", data={"csrf_value": csrf}, files={"file": ("test.csv", raw, "text/csv")}
    )
    assert first.status_code == 200
    second = client.post(
        "/imports", data={"csrf_value": csrf}, files={"file": ("test.csv", raw, "text/csv")}
    )
    assert second.url == first.url
    assert (
        client.post(
            "/imports", data={"csrf_value": csrf}, files={"file": ("bad.csv", b"bad", "text/csv")}
        ).status_code
        == 400
    )
    assert client.post("/imports/1/replay", data={"csrf_value": "bad"}).status_code == 403
    assert client.get("/imports/1/export").status_code == 200


def test_login_throttle(client):
    csrf = token(client, "/login")
    for _ in range(5):
        assert (
            client.post(
                "/login",
                data={
                    "csrf_value": csrf,
                    "email": "unknown@test.demo",
                    "password": "wrong",
                },
            ).status_code
            == 400
        )
    assert (
        client.post(
            "/login", data={"csrf_value": csrf, "email": "unknown@test.demo", "password": "wrong"}
        ).status_code
        == 429
    )


def test_successful_signins_do_not_accumulate_throttle(client):
    for _ in range(7):
        sign_in(client)
