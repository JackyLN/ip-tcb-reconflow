"""Grading, scoped accounting, incremental persistence and read-only evaluation exports."""

from decimal import Decimal

import httpx
import pytest
from conftest import sign_in
from sqlalchemy import select

from reconflow import evaluation
from reconflow.config import settings
from reconflow.db import SessionLocal
from reconflow.models import Control, Evaluation, Invocation
from reconflow.services.ai import simulated_report


def configure_live(monkeypatch):
    monkeypatch.setattr(settings(), "llm_api_key", "unit-test-placeholder")
    monkeypatch.setattr(settings(), "llm_model", "mock-model")


def test_grading_errors_and_run_scoped_usage(monkeypatch):
    configure_live(monkeypatch)
    calls = []

    def provider(db, case_id, tools, **kwargs):
        index = len(calls)
        calls.append(case_id)
        db.add(
            Invocation(
                model="mock-model",
                status="TRANSPORT_ERROR" if index == 2 else "RECEIVED_UNVALIDATED",
                latency_ms=10,
                input_tokens=0 if index == 2 else 100,
                output_tokens=0 if index == 2 else 20,
                cost_usd="0" if index == 2 else "0.001",
            )
        )
        if index == 2:
            raise httpx.ReadTimeout("A sensitive provider message must not be persisted")
        label = "AMBIGUOUS" if index == 1 else "FEE_MISMATCH"
        refs = ["evidence:UNSEEN"] if index == 3 else [tools["get_case"]["evidence_id"]]
        return simulated_report(case_id, label, refs), []

    monkeypatch.setattr(evaluation, "live_report", provider)
    with SessionLocal.begin() as db:
        unrelated = Invocation(
            model="other-run", status="RECEIVED_UNVALIDATED", latency_ms=1, cost_usd="10"
        )
        db.add(unrelated)
        result = evaluation.evaluate(db, live=True, limit=4)
        assert result["status"] == "COMPLETED"
        assert result["model_correct"] == 1 and result["model_accuracy"] == 0.25
        assert result["schema_and_evidence_valid"] == 2
        assert len(result["failures"]) == 3
        assert {c["failure_reason"] for c in result["failures"]} == {
            "LABEL_MISMATCH",
            "PROVIDER_TIMEOUT",
            "EVIDENCE_REFERENCE_REJECTED",
        }
        assert result["usage"]["requests"] == 4
        assert result["usage"]["input_tokens"] == 300
        assert Decimal(result["usage"]["estimated_usd"]) == Decimal("0.003")
        assert result["usage"]["unmetered_requests"] == 1
        assert unrelated.id not in [i for c in result["cases"] for i in c["invocation_ids"]]
        assert "sensitive" not in str(result)


def test_checkpoint_retains_completed_cases_after_interruption(monkeypatch):
    configure_live(monkeypatch)
    calls = []

    def provider(db, case_id, tools, **kwargs):
        if calls:
            raise KeyboardInterrupt()
        calls.append(case_id)
        return simulated_report(case_id, "FEE_MISMATCH", [tools["get_case"]["evidence_id"]]), []

    monkeypatch.setattr(evaluation, "live_report", provider)
    with SessionLocal() as db, pytest.raises(KeyboardInterrupt):
        evaluation.evaluate(db, live=True, limit=2, checkpoint=True)
    with SessionLocal() as db:
        result = db.scalar(select(Evaluation)).results
        assert result["status"] == "RUNNING" and result["cases_run"] == 1
        assert len(result["cases"]) == 1


def test_live_eval_respects_kill_switch(monkeypatch):
    configure_live(monkeypatch)
    monkeypatch.setattr(
        evaluation, "live_report", lambda *args, **kwargs: pytest.fail("No provider call permitted")
    )
    with SessionLocal.begin() as db:
        db.get(Control, 1).ai_enabled = False
        result = evaluation.evaluate(db, live=True)
        assert result["status"] == "STOPPED_KILL_SWITCH" and result["cases_run"] == 0


def test_eval_dashboard_export_and_offline_separation(client):
    with SessionLocal.begin() as db:
        result = evaluation.evaluate(db, limit=2)
        run_id = result["evaluation_id"]
    response = client.get(f"/ai/evaluation/{run_id}/export", follow_redirects=False)
    assert response.status_code in (303, 401)
    sign_in(client, "auditor")
    page = client.get("/ai/evaluation")
    assert page.status_code == 200
    assert "Model accuracy, latency and abstention quality are not measured" in page.text
    exported = client.get(f"/ai/evaluation/{run_id}/export")
    assert exported.status_code == 200
    assert exported.json()["model_correct"] is None
    assert "attachment" in exported.headers["content-disposition"]
    assert client.get("/ai/evaluation/99999/export").status_code == 404


def test_fixture_split_is_disjoint_and_expected_labels_are_not_tool_inputs():
    fixtures = evaluation.dataset()
    development = {c["id"] for c in fixtures if c["split"] == "development"}
    holdout = [c for c in fixtures if c["split"] == "holdout"]
    assert not development & {c["id"] for c in holdout}
    assert len(holdout) == 48
    for c in holdout:
        assert "expected" not in c["tools"]["get_case"]
        assert "rule_finding" not in c["tools"]["get_case"]
        assert evaluation.deterministic_baseline(c["tools"]) == c["expected"]


def test_live_dashboard_shows_graded_scores_and_case_details(client, monkeypatch):
    configure_live(monkeypatch)

    def provider(db, case_id, tools, **kwargs):
        return simulated_report(case_id, "FEE_MISMATCH", [tools["get_case"]["evidence_id"]]), []

    monkeypatch.setattr(evaluation, "live_report", provider)
    with SessionLocal.begin() as db:
        result = evaluation.evaluate(db, live=True, limit=2)
    sign_in(client)
    response = client.get("/ai/evaluation")
    assert response.status_code == 200
    assert "100.0%" in response.text and "Per-class grading" in response.text
    assert "No classification or validation failures" in response.text
    assert result["dataset_sha256"] in response.text


def test_snapshot_sync_is_idempotent_and_remaps_only_evaluation_usage(monkeypatch):
    from sqlalchemy import func

    from reconflow.models import Case
    from scripts.evaluation_snapshot import export_snapshot, import_snapshot

    configure_live(monkeypatch)

    def provider(db, case_id, tools, **kwargs):
        db.add(
            Invocation(
                model="mock-model",
                status="RECEIVED_UNVALIDATED",
                latency_ms=10,
                input_tokens=100,
                output_tokens=20,
                cost_usd="0.001",
            )
        )
        return simulated_report(case_id, "FEE_MISMATCH", [tools["get_case"]["evidence_id"]]), []

    monkeypatch.setattr(evaluation, "live_report", provider)
    with SessionLocal.begin() as db:
        result = evaluation.evaluate(db, live=True, limit=1)
        payload = export_snapshot(db, result["evaluation_id"], "production-demo")
        case_count = db.scalar(select(func.count()).select_from(Case))
        imported_id = import_snapshot(db, payload)
        assert import_snapshot(db, payload) == imported_id
        imported = db.get(Evaluation, imported_id).results
        assert imported["sync_origin"] == "production-demo"
        assert imported["source_evaluation_id"] == result["evaluation_id"]
        assert (
            imported["cases"][0]["invocation_ids"]
            != payload["results"]["cases"][0]["invocation_ids"]
        )
        assert db.scalar(select(func.count()).select_from(Case)) == case_count
        assert imported["usage"] == result["usage"]
        assert "sync_origin" not in payload["results"]
