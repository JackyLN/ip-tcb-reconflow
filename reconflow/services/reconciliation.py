"""Deterministic payout aggregation and conservative single-credit matching."""

from datetime import timedelta
from time import perf_counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from reconflow.models import BankCredit, Case, Match, Payment, Payout, Provider, Run
from reconflow.services.audit import append
from reconflow.services.money import fee, net


def reconcile(db: Session, run_id: int, actor: int) -> None:
    run = db.get(Run, run_id)
    if run.status == "COMPLETED":
        return
    start = perf_counter()
    run.status = "RUNNING"
    payouts = db.scalars(select(Payout).where(Payout.import_id == run.import_id)).all()
    for payout in payouts:
        if db.scalar(select(Match.id).where(Match.payout_id == payout.id)):
            continue
        payments = db.scalars(select(Payment).where(Payment.payout_id == payout.id)).all()
        gross = sum(p.amount for p in payments)
        refunds = sum(p.refund for p in payments)
        expected = net(gross, refunds, payout.fee, payout.adjustment)
        policy = db.get(Provider, payout.provider_id)
        candidates = db.scalars(
            select(BankCredit).where(
                BankCredit.reference == payout.external_id,
                BankCredit.account == payout.account,
                BankCredit.import_id == payout.import_id,
            )
        ).all()
        reference_collisions = db.scalar(
            select(func.count())
            .select_from(Payout)
            .where(
                Payout.import_id == payout.import_id,
                Payout.account == payout.account,
                Payout.external_id == payout.external_id,
            )
        )
        status = "MATCHED"
        if len(candidates) > 1 or reference_collisions > 1:
            status = "AMBIGUOUS"
        elif not candidates:
            status = "MISSING_CREDIT"
        elif candidates[0].currency != payout.currency:
            status = "CURRENCY_MISMATCH"
        elif (
            not payout.settled_at
            <= candidates[0].booked_at
            <= payout.settled_at + timedelta(days=3)
        ):
            status = "LATE_CREDIT"
        elif abs(payout.fee - fee(gross, policy.fee_bps)) > policy.tolerance:
            status = "FEE_MISMATCH"
        elif expected != payout.declared_net:
            status = "PAYOUT_MISMATCH"
        elif candidates[0].amount != expected:
            status = "AMOUNT_MISMATCH"
        evidence = {
            "gross": gross,
            "refunds": refunds,
            "fees": payout.fee,
            "adjustment": payout.adjustment,
            "expected": expected,
            "declared_net": payout.declared_net,
            "policy_fee": fee(gross, policy.fee_bps),
            "policy_version": policy.policy_version,
            "candidate_ids": [c.id for c in candidates],
            "payment_count": len(payments),
            "reference_collisions": reference_collisions,
        }
        db.add(
            Match(
                payout_id=payout.id,
                run_id=run.id,
                expected=expected,
                status=status,
                credit_id=candidates[0].id if status == "MATCHED" else None,
                rationale=f"{status}: gross - refunds - provider fee + adjustment; "
                "one reference/account/currency credit within 3 days required.",
                evidence=evidence,
            )
        )
        if status != "MATCHED":
            db.add(Case(payout_id=payout.id, classification=status))
    run.status = "COMPLETED"
    run.elapsed_ms = max(1, int((perf_counter() - start) * 1000))
    append(
        db,
        actor,
        "reconciliation.completed",
        f"run:{run.id}",
        payouts=len(payouts),
        elapsed_ms=run.elapsed_ms,
        rule=run.rule_version,
    )
