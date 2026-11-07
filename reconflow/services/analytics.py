"""Measured database reports and separately labeled assumption-based projections."""

from decimal import Decimal
from statistics import median

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from reconflow.db import now
from reconflow.models import Case, Match, Payment, Payout, Proposal, Run


def count(db: Session, model: type) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def overview(db: Session) -> dict:
    matches = db.scalars(select(Match)).all()
    cases = db.scalars(select(Case)).all()
    # Current snapshot, eligibility = every processed payout. Routed = persisted exception.
    matched = sum(m.status == "MATCHED" for m in matches)
    routed = sum(c.status in ("NEEDS_REVIEW", "RESOLVED", "ESCALATED") for c in cases)
    runs = db.scalars(select(Run).where(Run.status == "COMPLETED")).all()
    return {
        "payments": count(db, Payment),
        "payouts": count(db, Payout),
        "matched": matched,
        "processed": len(matches),
        "open": sum(c.status != "RESOLVED" for c in cases),
        "pending": db.scalar(
            select(func.count()).select_from(Proposal).where(Proposal.status == "PENDING")
        )
        or 0,
        "median_ms": int(median(r.elapsed_ms for r in runs)) if runs else None,
        "north_star_numerator": matched + routed,
        "north_star_denominator": len(matches),
        "distribution": {
            s: sum(m.status == s for m in matches) for s in sorted({m.status for m in matches})
        },
        "oldest_hours": max(
            (
                (now() - c.created_at).total_seconds() / 3600
                for c in cases
                if c.status != "RESOLVED"
            ),
            default=0,
        ),
    }


def impact(
    volume: int,
    minutes: int,
    hourly: int,
    adoption: int,
    automation: int,
    implementation: int,
    monthly_cost: int,
) -> dict:
    """All inputs are assumptions in USD. Decimal projection, no financial floats."""
    if not (
        0 <= volume <= 10_000_000
        and 0 <= minutes <= 480
        and 0 <= hourly <= 1000
        and 0 <= adoption <= 100
        and 0 <= automation <= 100
        and 0 <= implementation <= 100_000_000
        and 0 <= monthly_cost <= 10_000_000
    ):
        raise ValueError("Assumptions outside supported ranges")
    monthly = Decimal(volume) * minutes / 60 * hourly * adoption / 100 * automation / 100
    cost = Decimal(implementation + 12 * monthly_cost)
    return {
        "annual_capacity": str((monthly * 12).quantize(Decimal("0.01"))),
        "annual_cost": str(cost),
        "net": str((monthly * 12 - cost).quantize(Decimal("0.01"))),
        "low_net": str((monthly * 12 * Decimal("0.5") - cost).quantize(Decimal("0.01"))),
        "high_net": str((monthly * 12 * Decimal("1.5") - cost).quantize(Decimal("0.01"))),
        "break_even_month": str((cost / monthly).quantize(Decimal("0.1"))) if monthly else "never",
    }
