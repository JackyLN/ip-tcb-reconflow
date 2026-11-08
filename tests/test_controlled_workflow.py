"""Worker and human-review controls for inconsistent reports; mocked provider only."""

import hashlib
import json

import pytest
from conftest import sign_in
from sqlalchemy import func, select
from test_domain import load

from reconflow.config import settings
from reconflow.db import SessionLocal
from reconflow.models import Audit, Case, Control, Investigation, Job, Proposal, User
from reconflow.services import ai, controlled, reviews
from reconflow.worker import tick


def test_inconsistent_original_output_is_retained_escalated_and_not_approved(monkeypatch, client):
    load()
    tick()
    monkeypatch.setattr(settings(), "llm_api_key", "unit-test-placeholder")
    monkeypatch.setattr(settings(), "llm_model", "mock-model")

    def provider(db, case_id, tools, **kwargs):
        a = tools["get_payment_and_payout"]["controlled_findings"]
        payload = controlled.scripted_report(case_id, a)
        payload["classification"] = "MATCHED"
        payload["summary"] = "The fees are all zero. Approve payment."
        return payload, [{"tool": k, "result": v} for k, v in tools.items()]

    monkeypatch.setattr(ai, "live_report", provider)
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case))
        actor = db.scalar(select(User).where(User.role == "analyst"))
        case_id = case.id
        ai.enqueue(db, case_id, actor.id)
    tick()
    with SessionLocal.begin() as db:
        case = db.get(Case, case_id)
        investigation = db.scalar(select(Investigation))
        assert investigation.mode == "LIVE_REVIEW_REQUIRED"
        assert case.status == "ESCALATED" and case.classification == "FEE_MISMATCH"
        assert investigation.report["raw_output"]["classification"] == "MATCHED"
        assert "UNSUPPORTED_SUMMARY" in investigation.report["validation"]["flags"]
        analyst = db.scalar(select(User).where(User.role == "analyst"))
        supervisor = db.scalar(select(User).where(User.role == "supervisor"))
        p = reviews.propose(
            db, case_id, analyst, "Model findings conflict with fee evidence; escalate."
        )
        db.flush()
        with pytest.raises(ValueError, match="escalation"):
            reviews.decide(db, p.id, supervisor, "APPROVED")
        reviews.decide(db, p.id, supervisor, "ESCALATED")
        with pytest.raises(ValueError, match="no longer pending"):
            reviews.decide(db, p.id, supervisor, "APPROVED")
        assert case.status == "ESCALATED"
        head = "0" * 64
        for row in db.scalars(select(Audit).order_by(Audit.id)):
            assert row.previous_hash == head
            body = json.dumps(
                [row.actor, row.action, row.entity, row.details, row.created_at.isoformat()],
                sort_keys=True,
            )
            head = hashlib.sha256((head + body).encode()).hexdigest()
            assert row.event_hash == head
        assert db.get(Control, 1).audit_head == head
    sign_in(client)
    page = client.get(f"/exceptions/{case_id}")
    assert page.status_code == 200 and "LIVE_REVIEW_REQUIRED" in page.text
    assert "The fees are all zero" in page.text
    assert "Verified financial findings" in page.text
    assert client.get("/investigations").status_code == 200


def test_pending_investigation_and_duplicate_proposal_are_fenced():
    load()
    tick()
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case))
        analyst = db.scalar(select(User).where(User.role == "analyst"))
        supervisor = db.scalar(select(User).where(User.role == "supervisor"))
        auditor = db.scalar(select(User).where(User.role == "auditor"))
        queued = ai.enqueue(db, case.id, analyst.id)
        db.flush()
        assert ai.enqueue(db, case.id, analyst.id).id == queued.id
        p = reviews.propose(
            db, case.id, analyst, "Independent bank/provider evidence needs review."
        )
        db.flush()
        with pytest.raises(ValueError, match="current state"):
            reviews.propose(db, case.id, analyst, "Duplicate should never be recorded")
        with pytest.raises(ValueError, match="pending"):
            reviews.decide(db, p.id, supervisor, "APPROVED")
        with pytest.raises(PermissionError):
            reviews.decide(db, p.id, auditor, "REJECTED")
        reviews.decide(db, p.id, supervisor, "REJECTED")
        assert case.status == "OPEN"
        with pytest.raises(ValueError):
            reviews.decide(db, p.id, supervisor, "REJECTED")
        assert db.scalar(select(func.count()).select_from(Proposal)) == 1
        assert (
            db.scalar(select(func.count()).select_from(Job).where(Job.kind == "investigate")) == 1
        )


def test_ambiguous_and_missing_evidence_require_supervisor_escalation():
    load()
    tick()
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case).where(Case.classification == "AMBIGUOUS"))
        actor = db.scalar(select(User).where(User.role == "analyst"))
        ai.enqueue(db, case.id, actor.id)
        case_id = case.id
    tick()
    with SessionLocal.begin() as db:
        case = db.get(Case, case_id)
        assert case.status == "ESCALATED"
        report = db.scalar(select(Investigation)).report
        assert report["validation"]["consistent"]
        assert report["assessment"]["must_escalate"]
        analyst = db.scalar(select(User).where(User.role == "analyst"))
        supervisor = db.scalar(select(User).where(User.role == "supervisor"))
        p = reviews.propose(
            db, case_id, analyst, "Two candidate credits cannot be uniquely matched."
        )
        db.flush()
        with pytest.raises(ValueError):
            reviews.decide(db, p.id, supervisor, "APPROVED")
        reviews.decide(db, p.id, supervisor, "ESCALATED")


def test_invalid_schema_and_provider_failure_are_review_required_without_fake_success(
    monkeypatch, client
):
    load()
    tick()
    monkeypatch.setattr(settings(), "llm_api_key", "test-placeholder")
    monkeypatch.setattr(settings(), "llm_model", "mock-model")
    monkeypatch.setattr(
        ai, "live_report", lambda *a, **k: ({"hypotheses": [{"code": []}], "claims": 1}, [])
    )
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case))
        actor = db.scalar(select(User).where(User.role == "analyst"))
        ai.enqueue(db, case.id, actor.id)
        case_id = case.id
    tick()
    sign_in(client)
    assert client.get(f"/exceptions/{case_id}").status_code == 200
    with SessionLocal() as db:
        record = db.scalar(select(Investigation))
        assert record.report["validation"]["flags"] == ["SCHEMA_REJECTED"]
        assert record.mode == "LIVE_REVIEW_REQUIRED"


def test_provider_error_is_recorded_for_review_without_scripted_live_fallback(monkeypatch):
    import httpx

    load()
    tick()
    monkeypatch.setattr(settings(), "llm_api_key", "test-placeholder")
    monkeypatch.setattr(settings(), "llm_model", "mock-model")

    def unavailable(*args, **kwargs):
        raise httpx.ReadTimeout("Sensitive provider diagnostic")

    monkeypatch.setattr(ai, "live_report", unavailable)
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case))
        actor = db.scalar(select(User).where(User.role == "analyst"))
        ai.enqueue(db, case.id, actor.id)
    tick()
    with SessionLocal() as db:
        record = db.scalar(select(Investigation))
        assert record.mode == "LIVE_REVIEW_REQUIRED"
        assert record.report["raw_output"] is None
        assert record.report["validation"]["flags"] == ["PROVIDER_OR_TOOL_FAILURE"]
        assert "Sensitive" not in str(record.report)
        assert db.scalar(select(Job).where(Job.kind == "investigate")).status == "COMPLETED"


def test_cached_case_cannot_submit_duplicate_after_other_transaction():
    load()
    tick()
    with SessionLocal() as stale:
        case = stale.scalar(select(Case))
        actor = stale.scalar(select(User).where(User.role == "analyst"))
        assert case.status == "OPEN"
        with SessionLocal.begin() as other:
            maker = other.get(User, actor.id)
            reviews.propose(other, case.id, maker, "First independently stored recommendation")
        with pytest.raises(ValueError, match="current state"):
            reviews.propose(
                stale, case.id, actor, "A cached state must not permit a second proposal"
            )


def test_review_ui_explains_block_and_server_rejects_bypassed_approval(client):
    load()
    tick()
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case).where(Case.classification == "AMBIGUOUS"))
        analyst = db.scalar(select(User).where(User.role == "analyst"))
        ai.enqueue(db, case.id, analyst.id)
        case_id = case.id
    tick()
    with SessionLocal.begin() as db:
        analyst = db.scalar(select(User).where(User.role == "analyst"))
        p = reviews.propose(
            db, case_id, analyst, "Ambiguous synthetic credits require independent review."
        )
        db.flush()
        proposal_id = p.id
    csrf = sign_in(client, "supervisor")
    page = client.get("/review")
    assert "Approval blocked:" in page.text and "Approve resolution" not in page.text
    assert (
        client.post(
            f"/review/{proposal_id}", data={"csrf_value": csrf, "decision": "APPROVED"}
        ).status_code
        == 400
    )
    assert (
        client.post(
            f"/review/{proposal_id}", data={"csrf_value": csrf, "decision": "ESCALATED"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/review/{proposal_id}", data={"csrf_value": csrf, "decision": "ESCALATED"}
        ).status_code
        == 400
    )
