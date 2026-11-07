"""Atomic, validated synthetic CSV imports with source identity conflict rejection."""

import csv
import hashlib
import io
import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from reconflow.models import BankCredit, ImportBatch, Job, Payment, Payout, Provider, Run
from reconflow.services.audit import append
from reconflow.services.money import EXPONENTS, fee, net

FIELDS = [
    "kind",
    "external_id",
    "payout_id",
    "provider",
    "currency",
    "account",
    "amount",
    "refund",
    "fee",
    "adjustment",
    "net",
    "timestamp",
]


def scenario_csv(count: int, scenario: str) -> str:
    """Fixed-RNG, fixed-time sources. Scenario names are never model ground truth."""
    if count not in (100, 1000, 10000) or scenario not in ("clean", "mismatch", "failure"):
        raise ValueError("Unsupported scenario")
    rng = random.Random(42)
    rows = []
    prefix = f"{scenario}-{count}"
    for batch in range(count // 20):
        pid = f"{prefix}-payout-{batch:04}"
        currency = "USD" if batch % 2 else "VND"
        amounts = [rng.randint(10000, 90000) for _ in range(20)]
        refunds = amounts[0] if batch % 7 == 0 else 0
        gross = sum(amounts)
        fees = fee(gross, 200)
        kind = batch % 7 if scenario != "clean" else 0
        declared_fee = fees + 100 if kind == 1 else fees
        expected = net(gross, refunds, declared_fee)
        common = dict(
            provider="SyntheticPay",
            currency=currency,
            account="SYNTH-001",
            timestamp="2026-01-15T09:00:00",
        )
        rows.append(
            dict(
                common, kind="payout", external_id=pid, fee=declared_fee, adjustment=0, net=expected
            )
        )
        for i, amount in enumerate(amounts):
            rows.append(
                dict(
                    common,
                    kind="payment",
                    external_id=f"{pid}-pay-{i}",
                    payout_id=pid,
                    amount=amount,
                    refund=refunds if i == 0 else 0,
                )
            )
        if kind == 2:  # missing credit
            continue
        credit = dict(
            common,
            kind="credit",
            external_id=f"{pid}-bank",
            payout_id=pid,
            amount=expected + (500 if kind == 3 else 0),
        )
        if kind == 4:
            credit["timestamp"] = "2026-01-21T09:00:00"
        rows.append(credit)
        if kind == 5:
            rows.append(dict(credit, external_id=f"{pid}-bank-duplicate"))
        if kind == 6:
            rows[-1]["currency"] = "USD" if currency == "VND" else "VND"
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def parse_csv(raw: str) -> list[dict]:
    """Reject malformed, fractional, excessive or unsupported input without partial writes."""
    if len(raw.encode()) > 8_000_000:
        raise ValueError("CSV exceeds 8 MB")
    reader = csv.DictReader(io.StringIO(raw))
    if reader.fieldnames != FIELDS:
        raise ValueError("CSV header must match the downloadable template exactly")
    rows = []
    seen = set()
    for line, row in enumerate(reader, 2):
        if line > 25000 or None in row or any(v is None for v in row.values()):
            raise ValueError(f"Row {line}: malformed or too many rows")
        if row["kind"] not in ("payment", "payout", "credit"):
            raise ValueError(f"Row {line}: unsupported record type")
        if row["currency"] not in EXPONENTS:
            raise ValueError(f"Row {line}: unsupported currency")
        for key in ("external_id", "provider", "account"):
            if (
                not row[key]
                or len(row[key]) > {"external_id": 100, "provider": 60, "account": 40}[key]
                or any(ord(c) < 32 for c in row[key])
            ):
                raise ValueError(f"Row {line}: invalid identifier")
        identity = (row["kind"], row["provider"], row["external_id"])
        if identity in seen:
            raise ValueError(f"Row {line}: duplicate source identity")
        seen.add(identity)
        for key in ("amount", "refund", "fee", "adjustment", "net"):
            value = row[key] or "0"
            if not value.lstrip("-").isdigit() or len(value) > 12:
                raise ValueError(f"Row {line}: amounts must be integer minor units")
            row[key] = int(value)
        if any(row[k] < 0 for k in ("amount", "refund", "fee", "net")):
            raise ValueError(f"Row {line}: invalid negative amount")
        if row["refund"] > row["amount"]:
            raise ValueError(f"Row {line}: refund exceeds payment")
        try:
            stamp = datetime.fromisoformat(row["timestamp"])
        except ValueError as exc:
            raise ValueError(f"Row {line}: invalid ISO timestamp") from exc
        if stamp.tzinfo is not None:
            raise ValueError("Timestamps must use UTC without an offset; see template")
        row["timestamp"] = stamp
        rows.append(row)
    if not rows or not any(r["kind"] == "payout" for r in rows):
        raise ValueError("CSV must contain payouts and linked payments")
    return rows


def ingest(db: Session, raw: str, name: str, actor: int, fail_once: bool = False) -> ImportBatch:
    """Caller owns transaction. Byte-identical replay returns existing batch/run/job."""
    digest = hashlib.sha256(raw.encode()).hexdigest()
    existing = db.scalar(select(ImportBatch).where(ImportBatch.digest == digest))
    if existing:
        append(db, actor, "import.replayed", f"import:{existing.id}")
        return existing
    rows = parse_csv(raw)
    source = ImportBatch(digest=digest, name=name[:120], raw_csv=raw)
    db.add(source)
    db.flush()
    providers = {p.name: p for p in db.scalars(select(Provider))}
    payouts = {}
    for row in rows:
        provider = providers.get(row["provider"])
        if not provider:
            raise ValueError("Unknown provider; admin must create its policy first")
        if row["kind"] != "payout":
            continue
        pid = (provider.id, row["external_id"])
        if db.scalar(
            select(Payout.id).where(
                Payout.provider_id == provider.id, Payout.external_id == row["external_id"]
            )
        ):
            raise ValueError("Existing payout identity in different source; replay original CSV")
        payout = Payout(
            provider_id=provider.id,
            import_id=source.id,
            external_id=row["external_id"],
            currency=row["currency"],
            account=row["account"],
            fee=row["fee"],
            adjustment=row["adjustment"],
            declared_net=row["net"],
            settled_at=row["timestamp"],
        )
        db.add(payout)
        db.flush()
        payouts[pid] = payout
    counts = {p.id: 0 for p in payouts.values()}
    for row in rows:
        provider = providers[row["provider"]]
        if row["kind"] == "payout":
            continue
        payout = payouts.get((provider.id, row["payout_id"]))
        if not payout:
            raise ValueError("Every payment and credit must reference an imported payout")
        if row["account"] != payout.account:
            raise ValueError("Account differs within payout")
        if row["kind"] == "payment":
            if row["currency"] != payout.currency:
                raise ValueError("Cross-currency payment aggregation unsupported")
            db.add(
                Payment(
                    provider_id=provider.id,
                    payout_id=payout.id,
                    external_id=row["external_id"],
                    amount=row["amount"],
                    refund=row["refund"],
                )
            )
            counts[payout.id] += 1
        else:
            db.add(
                BankCredit(
                    external_id=row["external_id"],
                    import_id=source.id,
                    reference=payout.external_id,
                    account=row["account"],
                    currency=row["currency"],
                    amount=row["amount"],
                    booked_at=row["timestamp"],
                )
            )
    if not all(counts.values()):
        raise ValueError("Payout without payment lines")
    run = Run(import_id=source.id)
    db.add(run)
    db.flush()
    db.add(
        Job(
            kind="reconcile",
            key=f"reconcile:{source.id}",
            actor_id=actor,
            payload={"run_id": run.id, "fail_once": fail_once},
        )
    )
    append(db, actor, "import.accepted", f"import:{source.id}", digest=digest, rows=len(rows))
    return source


def safe_csv(raw: str) -> str:
    """Prevent spreadsheet formulas in exported untrusted string cells."""
    out = io.StringIO()
    writer = csv.writer(out)
    for row in csv.reader(io.StringIO(raw)):
        writer.writerow(
            [
                "'" + cell if cell.startswith(("=", "+", "-", "@", "\t", "\r")) else cell
                for cell in row
            ]
        )
    return out.getvalue()


def scenario_labels(count: int, scenario: str) -> str:
    """Intended synthetic payout labels, separate from observed reconciliation/model outputs."""
    scenario_csv(count, scenario)  # validate generator choices
    labels = [
        "MATCHED",
        "FEE_MISMATCH",
        "MISSING_CREDIT",
        "AMOUNT_MISMATCH",
        "LATE_CREDIT",
        "AMBIGUOUS",
        "CURRENCY_MISMATCH",
    ]
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["payout_external_id", "expected_finding", "provenance"])
    for batch in range(count // 20):
        writer.writerow(
            [
                f"{scenario}-{count}-payout-{batch:04}",
                "MATCHED" if scenario == "clean" else labels[batch % 7],
                "SYNTHETIC_GENERATOR_LABEL_NOT_MODEL_OUTPUT",
            ]
        )
    return out.getvalue()
