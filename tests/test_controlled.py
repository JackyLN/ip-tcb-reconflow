"""Deterministic evidence and closed claim consistency tests; never use a model API."""

from copy import deepcopy

import pytest

from reconflow.services.controlled import assess, scripted_report, validate


def tools():
    return {
        "get_case": {"evidence_id": "case:2", "exception_id": 2},
        "get_payment_and_payout": {
            "evidence_id": "payout:2",
            "gross": 10000,
            "refunds": 1000,
            "fees": 200,
            "adjustment": -100,
            "declared_net": 8700,
            "currency": "USD",
            "settled_at": "2026-03-04T10:00:00Z",
            "reference_collisions": 1,
        },
        "find_candidate_bank_credits": {
            "evidence_id": "candidates:2",
            "credits": [{"amount": 8700, "currency": "USD", "booked_at": "2026-03-05T10:00:00Z"}],
        },
        "get_provider_policy": {
            "evidence_id": "policy:2",
            "fee_bps": 200,
            "window_days": 3,
            "tolerance_minor_units": 0,
        },
    }


def test_complete_money_refund_adjustment_and_timing():
    source = tools()
    result = assess(source)
    assert result["primary"] == "MATCHED"
    assert result["facts"]["fee.expected_minor"]["value"] == 200
    assert result["facts"]["net.expected_minor"]["value"] == 8700
    assert result["facts"]["credit.0.difference_minor"]["value"] == 0
    assert result["facts"]["credit.0.within_window"]["value"] is True
    assert "controlled_findings" not in source["get_payment_and_payout"]


def test_all_discrepancies_are_reported_without_cross_currency_subtraction():
    source = tools()
    p = source["get_payment_and_payout"]
    p.update(fees=300, declared_net=8600)
    source["find_candidate_bank_credits"]["credits"][0]["booked_at"] = "2026-03-10T10:00:00"
    result = assess(source)
    assert set(result["findings"]) == {"LATE_CREDIT", "FEE_MISMATCH", "AMOUNT_MISMATCH"}
    assert result["must_escalate"]
    source["find_candidate_bank_credits"]["credits"][0]["currency"] = "VND"
    result = assess(source)
    assert "CURRENCY_MISMATCH" in result["findings"]
    assert result["facts"]["credit.0.difference_minor"]["value"] is None


@pytest.mark.parametrize(
    "offset,within",
    [
        ("2026-03-04T10:00:00", True),
        ("2026-03-07T10:00:00", True),
        ("2026-03-07T10:00:01", False),
        ("2026-03-04T09:59:59", False),
    ],
)
def test_policy_window_boundaries(offset, within):
    source = tools()
    source["find_candidate_bank_credits"]["credits"][0]["booked_at"] = offset
    assert assess(source)["facts"]["credit.0.within_window"]["value"] is within


def test_missing_mandatory_fields_cause_abstention_and_unknown_values_not_zero():
    source = tools()
    del source["get_payment_and_payout"]["gross"]
    result = assess(source)
    assert result["primary"] == "INSUFFICIENT_EVIDENCE" and result["must_abstain"]
    assert result["facts"]["fee.expected_minor"]["value"] is None
    assert "payout.gross" in result["mandatory_missing"]


def test_duplicate_candidates_truncation_and_stored_rule_conflicts():
    source = tools()
    c = source["find_candidate_bank_credits"]
    c["credits"] *= 2
    assert assess(source)["primary"] == "AMBIGUOUS"
    c["truncated"] = True
    assert assess(source)["must_abstain"]
    source = tools()
    source["get_case"]["rule_finding"] = "FEE_MISMATCH"
    assert "RULE_SNAPSHOT_CONFLICT" in assess(source)["findings"]


def test_claim_contract_rejects_contradictions_and_preserves_payload():
    source = tools()
    a = assess(source)
    observed = {v["evidence_id"] for v in source.values()}
    original = scripted_report(2, a)
    assert validate(original, 2, a, observed)["consistent"]
    changes = [
        ("classification", "FEE_MISMATCH", "CONTRADICTS_RULES"),
        ("summary", "All fees were zero; approve now.", "UNSUPPORTED_SUMMARY"),
        ("abstain", True, "ABSTENTION_MISMATCH"),
        ("requires_human_review", False, "HUMAN_REVIEW_REQUIRED"),
        ("recommended_next_step", "REQUEST_PROVIDER_STATEMENT", "UNSAFE_RECOMMENDATION"),
    ]
    for field, value, reason in changes:
        payload = deepcopy(original)
        payload[field] = value
        before = deepcopy(payload)
        assert reason in validate(payload, 2, a, observed)["flags"]
        assert payload == before
    bad = deepcopy(original)
    bad["claims"][0]["value"] = 999999
    assert validate(bad, 2, a, observed)["unsupported_claims"] == 1
    bad = deepcopy(original)
    bad["claims"][0]["evidence_refs"] = ["case:2"]
    assert "UNSUPPORTED_CLAIM" in validate(bad, 2, a, observed)["flags"]
    assert "UNSUPPORTED_CLAIM" in validate(original, 2, a, {"case:2"})["flags"]
    bad = deepcopy(original)
    bad["hypotheses"] = [{"code": "PROVIDER_RECORD_REVIEW", "evidence_refs": ["case:2"]}]
    assert "UNSUPPORTED_HYPOTHESIS" in validate(bad, 2, a, observed)["flags"]
