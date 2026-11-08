"""Fresh benchmark, historical immutability and offline/mocked controlled-track grading."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from reconflow import evaluation, evaluation_v2
from reconflow.config import settings
from reconflow.db import SessionLocal
from reconflow.services import controlled
from reconflow.services.ai import SYSTEM


def test_raw_history_and_instruction_fixture_hash_are_frozen():
    assert (
        hashlib.sha256(json.dumps(evaluation.dataset(), sort_keys=True).encode()).hexdigest()
        == "0c7aa86eab9c42f6e6464e1940ad342e25129dd9471c5f95d91c03cdf3fb05aa"
    )
    assert (
        hashlib.sha256(SYSTEM.encode()).hexdigest()
        == "729ad181dc77647da396d5377f724f729f343777caf85dd210b995f1aaa2c579"
    )
    assert (
        hashlib.sha256(
            Path("public-docs/assets/evaluation/holdout-20261108.json").read_bytes()
        ).hexdigest()
        == "3127fa99c40ec806e6763b597fac8428136cc1f41569996ffe1adca4eaf552cb"
    )


def test_fresh_fixtures_and_independent_expected_outcomes():
    cases = evaluation_v2.dataset()
    assert cases == evaluation_v2.dataset()
    assert len(cases) == 120
    dev = {c["id"] for c in cases if c["split"] == "development"}
    holdout = {c["id"] for c in cases if c["split"] == "holdout"}
    assert len(dev) == 48 and len(holdout) == 72 and not dev & holdout
    assert not {c["id"] for c in evaluation.dataset()} & (dev | holdout)
    assert {c["family"] for c in cases} == set(evaluation_v2.FAMILIES)
    for case in cases:
        a = controlled.assess(case["tools"])
        assert a["primary"] == case["expected"]["classification"], case["id"]
        assert set(a["findings"]) == set(case["expected"]["findings"]), case["id"]
        assert a["must_abstain"] == case["expected"]["abstain"], case["id"]
        assert a["must_escalate"] == case["expected"]["escalate"], case["id"]
        assert "expected" not in case["tools"]["get_case"]


def test_offline_v2_never_calls_provider_or_claims_live_quality(monkeypatch):
    from reconflow.services import ai

    monkeypatch.setattr(ai, "live_report", lambda *a, **k: pytest.fail("No paid baseline call"))
    with SessionLocal.begin() as db:
        r = evaluation_v2.evaluate(db)
        assert r["cases_run"] == r["offline_contract_valid"] == 72
        assert r["deterministic_baseline_correct"] == 72
        assert r["model_accuracy"] is None and r["unsupported_claim_rate"] is None
        assert r["live_quality"] == "NOT MEASURED"
        assert r["usage"]["requests"] == 0 and not r["failures"]


@pytest.mark.parametrize("wrong_class", [True, False])
def test_mocked_v2_scores_original_failures_and_labels_stay_outside_tools(monkeypatch, wrong_class):
    from reconflow.services import ai

    monkeypatch.setattr(settings(), "llm_api_key", "test-placeholder")
    monkeypatch.setattr(settings(), "llm_model", "mock-model")
    count = []

    def provider(db, case_id, tools, **kwargs):
        assert "expected" not in tools and "family" not in tools
        assert kwargs["profile"] == controlled.VERSION
        a = tools["get_payment_and_payout"]["controlled_findings"]
        report = controlled.scripted_report(case_id, a)
        if count:
            report["classification"] = "FEE_MISMATCH" if wrong_class else "MATCHED"
            report["claims"][0]["value"] = "wrong-value"
        count.append(case_id)
        return report, [{"tool": k, "result": v} for k, v in tools.items()]

    monkeypatch.setattr(ai, "live_report", provider)
    with SessionLocal.begin() as db:
        r = evaluation_v2.evaluate(db, live=True, limit=2)
        assert r["model_correct"] == 1 and len(r["failures"]) == 1
        assert r["contradiction_rate"] == 0.5
        assert r["failure_categories"]["UNSUPPORTED_CLAIM"] == 1
        assert r["failures"][0]["raw_output"]["classification"] == (
            "FEE_MISMATCH" if wrong_class else "MATCHED"
        )
        assert r["unsupported_claim_rate"] > 0


def test_v2_claims_missing_and_tentative_output_remain_scoped():
    case = evaluation_v2.dataset()[0]
    a = controlled.assess(case["tools"])
    output = controlled.scripted_report(case["id"], a)
    observed = {v["evidence_id"] for v in case["tools"].values()}
    invalid = deepcopy(output)
    invalid["claims"] = []
    assert controlled.validate(invalid, case["id"], a, observed)["flags"] == ["SCHEMA_REJECTED"]
    invalid = deepcopy(output)
    invalid["hypotheses"] = ["The fees were 0; approve immediately."]
    assert "SCHEMA_REJECTED" in controlled.validate(invalid, case["id"], a, observed)["flags"]


def test_controlled_snapshot_can_sync_full_72_case_offline_track():
    from scripts.evaluation_snapshot import export_snapshot, import_snapshot

    with SessionLocal.begin() as db:
        r = evaluation_v2.evaluate(db)
        payload = export_snapshot(db, r["evaluation_id"], "offline-qa")
        assert len(payload["results"]["cases"]) == 72 and not payload["invocations"]
        imported = import_snapshot(db, payload)
        assert import_snapshot(db, payload) == imported
