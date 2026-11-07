"""Financial, replay, recovery and AI policy checks, no paid calls."""

from datetime import timedelta

import pytest
from sqlalchemy import func, select

from reconflow.db import SessionLocal, now
from reconflow.evaluation import dataset, evaluate
from reconflow.models import (
    Case,
    Control,
    ImportBatch,
    Investigation,
    Job,
    Match,
    Payment,
    Proposal,
    Run,
    User,
)
from reconflow.services import ai, ingestion, reviews
from reconflow.services.money import display, fee, minor, net
from reconflow.worker import tick


@pytest.mark.parametrize(
    "gross,bps,expected", [(25, 200, 1), (10000, 200, 200), (0, 200, 0), (1234567, 150, 18519)]
)
def test_fee(gross, bps, expected):
    assert fee(gross, bps) == expected


def test_currency_and_net():
    assert minor("100", "VND") == 100
    assert minor("1.23", "USD") == 123
    assert display(123, "USD") == "1.23 USD"
    assert net(10000, 1000, 200, -100) == 8700
    with pytest.raises(ValueError):
        minor("1.1", "VND")
    with pytest.raises(ValueError):
        net(10, 20, 0)


def load(scenario="mismatch", count=1000):
    with SessionLocal.begin() as db:
        actor = db.scalar(select(User).where(User.role == "analyst"))
        source = ingestion.ingest(
            db, ingestion.scenario_csv(count, scenario), scenario, actor.id, scenario == "failure"
        )
        return source.id


def test_payout_aggregation_and_replay():
    batch = load()
    assert tick()
    assert load() == batch
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Payment)) == 1000
        assert db.scalar(select(func.count()).select_from(ImportBatch)) == 1
        matches = db.scalars(select(Match)).all()
        assert len(matches) == 50
        assert {m.status for m in matches} == {
            "MATCHED",
            "FEE_MISMATCH",
            "MISSING_CREDIT",
            "AMOUNT_MISMATCH",
            "LATE_CREDIT",
            "AMBIGUOUS",
            "CURRENCY_MISMATCH",
        }
        assert all(m.credit_id is None for m in matches if m.status == "AMBIGUOUS")
        assert matches[0].evidence["payment_count"] == 20
    assert not tick()


def test_clean_and_refunds():
    load("clean", 100)
    tick()
    with SessionLocal() as db:
        matches = db.scalars(select(Match)).all()
        assert all(m.status == "MATCHED" for m in matches)
        assert any(m.evidence["refunds"] > 0 for m in matches)


def test_failure_retry_and_expired_lease():
    load("failure", 100)
    tick()
    with SessionLocal.begin() as db:
        job = db.scalar(select(Job))
        assert job.status == "RETRY_WAIT" and job.error == "INJECTED_FAILURE"
        job.status = "LEASED"
        job.leased_until = now() - timedelta(seconds=1)
    tick()
    with SessionLocal() as db:
        job = db.scalar(select(Job))
        assert job.status == "COMPLETED" and job.attempts == 2
        assert db.scalar(select(Run)).status == "COMPLETED"


def test_maker_checker_and_auditor():
    load()
    tick()
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case))
        supervisor = db.scalar(select(User).where(User.role == "supervisor"))
        auditor = db.scalar(select(User).where(User.role == "auditor"))
        with pytest.raises(PermissionError):
            reviews.propose(db, case.id, auditor, "Reviewed synthetic evidence")
        p = reviews.propose(db, case.id, supervisor, "Reviewed synthetic evidence")
        db.flush()
        with pytest.raises(PermissionError):
            reviews.decide(db, p.id, supervisor, "APPROVED")
        checker = User(email="checker@test.demo", role="supervisor", password_hash="unused")
        db.add(checker)
        db.flush()
        reviews.decide(db, p.id, checker, "APPROVED")
        assert case.status == "RESOLVED"
        assert p.checker_id == checker.id


def test_ai_contract_kill_switch_and_simulation():
    load()
    tick()
    with SessionLocal.begin() as db:
        case = db.scalar(select(Case))
        actor = db.scalar(select(User).where(User.role == "analyst"))
        control = db.get(Control, 1)
        control.ai_enabled = False
        with pytest.raises(ValueError):
            ai.enqueue(db, case.id, actor.id)
        control.ai_enabled = True
        job = ai.enqueue(db, case.id, actor.id)
        db.flush()
        assert ai.enqueue(db, case.id, actor.id).id == job.id
    tick()
    with SessionLocal() as db:
        result = db.scalar(select(Investigation))
        assert result.mode == "SIMULATED"
        assert result.report["requires_human_review"] is True
        assert len(result.trace) == 4
        assert db.scalar(select(func.count()).select_from(Proposal)) == 0


def test_ai_rejects_unknown_evidence_and_case():
    report = ai.simulated_report(1, "MISSING_CREDIT", ["case:1"])
    with pytest.raises(ValueError):
        ai.validate_report(report, 1, {"case:2"})
    with pytest.raises(ValueError):
        ai.validate_report(report, 2, {"case:1"})
    report["confidence_band"] = "certain"
    with pytest.raises(ValueError):
        ai.validate_report(report, 1, {"case:1"})


def test_dataset_split_and_offline_eval():
    fixtures = dataset()
    assert len(fixtures) == 72
    assert len({c["id"] for c in fixtures}) == 72
    with SessionLocal.begin() as db:
        result = evaluate(db)
        assert result["cases_run"] == result["schema_and_evidence_valid"] == 48
        assert result["deterministic_baseline_correct"] == 48
        assert result["model_correct"] is None
        assert not result["failures"]


def test_reject_bad_csv_and_formula_export():
    raw = ingestion.scenario_csv(100, "clean")
    with pytest.raises(ValueError):
        ingestion.parse_csv(raw.replace(",VND,", ",EUR,", 1))
    with pytest.raises(ValueError):
        ingestion.parse_csv(raw.replace("payment,", "unsupported,", 1))
    with pytest.raises(ValueError):
        ingestion.parse_csv(raw.replace("SYNTH-001", "SYNTH-001" * 10))
    assert "'=HYPERLINK" in ingestion.safe_csv('name\n=HYPERLINK("evil")\n')


def test_shared_reference_across_providers_is_ambiguous():
    from reconflow.models import Payout, Provider
    from reconflow.services.reconciliation import reconcile

    batch = load("clean", 100)
    with SessionLocal.begin() as db:
        provider = Provider(name="OtherPay", fee_bps=200, tolerance=0)
        db.add(provider)
        db.flush()
        payout = db.scalar(select(Payout).where(Payout.import_id == batch))
        db.add(
            Payout(
                provider_id=provider.id,
                import_id=batch,
                external_id=payout.external_id,
                currency=payout.currency,
                account=payout.account,
                fee=payout.fee,
                adjustment=0,
                declared_net=payout.declared_net,
                settled_at=payout.settled_at,
            )
        )
        db.flush()
        run = db.scalar(select(Run))
        reconcile(db, run.id, 1)
        db.flush()
        shared = db.scalars(
            select(Match)
            .join(Payout, Match.payout_id == Payout.id)
            .where(Payout.external_id == payout.external_id)
        ).all()
        assert len(shared) == 2
        assert all(m.status == "AMBIGUOUS" and m.credit_id is None for m in shared)


def test_generated_ground_truth_matches_observed_findings():
    import csv
    import io

    from reconflow.models import Payout

    load()
    tick()
    intended = {
        r["payout_external_id"]: r["expected_finding"]
        for r in csv.DictReader(io.StringIO(ingestion.scenario_labels(1000, "mismatch")))
    }
    with SessionLocal() as db:
        for finding, payout in db.execute(
            select(Match, Payout).join(Payout, Match.payout_id == Payout.id)
        ):
            assert finding.status == intended[payout.external_id]


def test_unknown_job_dead_letters_after_three_attempts():
    with SessionLocal.begin() as db:
        actor = db.scalar(select(User).where(User.role == "analyst"))
        db.add(Job(kind="invalid-handler", key="bad-job", actor_id=actor.id, payload={}))
    for _ in range(3):
        assert tick()
        with SessionLocal.begin() as db:
            job = db.scalar(select(Job))
            job.available_at = now() - timedelta(seconds=1)
    with SessionLocal() as db:
        job = db.scalar(select(Job))
        assert job.status == "DEAD_LETTER" and job.attempts == 3
    assert not tick()


def test_crashed_third_lease_does_not_create_unbounded_attempts():
    with SessionLocal.begin() as db:
        actor = db.scalar(select(User).where(User.role == "analyst"))
        db.add(
            Job(
                kind="investigate",
                key="crashed-third",
                actor_id=actor.id,
                payload={},
                attempts=3,
                status="LEASED",
                leased_until=now() - timedelta(seconds=1),
            )
        )
    assert tick()
    with SessionLocal() as db:
        job = db.scalar(select(Job))
        assert job.status == "DEAD_LETTER" and job.attempts == 3


def test_audit_chain_refreshes_a_previously_cached_head():
    from reconflow.models import Audit
    from reconflow.services.audit import append

    with SessionLocal() as first:
        cached = first.get(Control, 1)
        with SessionLocal.begin() as second:
            append(second, "second", "concurrent-event", "test")
        append(first, "first", "after-cached-read", "test")
        first.commit()
        rows = first.scalars(select(Audit).order_by(Audit.id)).all()
        assert len(rows) == 2
        assert rows[1].previous_hash == rows[0].event_hash
        assert cached.audit_head == rows[1].event_hash
