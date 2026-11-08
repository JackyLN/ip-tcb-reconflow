"""Export/import only synthetic evaluation records and usage; never keys or finance records."""

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from reconflow.config import settings
from reconflow.db import SessionLocal
from reconflow.models import Evaluation, Invocation

SCHEMA = "reconflow-evaluation-v1"


def export_snapshot(db: Session, evaluation_id: int, origin: str) -> dict:
    """Select the run and its explicitly scoped request IDs; no configuration/credential export."""
    evaluation = db.get(Evaluation, evaluation_id)
    if not evaluation or "cases" not in evaluation.results:
        raise ValueError("A checkpointed evaluation record is required")
    ids = {i for case in evaluation.results["cases"] for i in case["invocation_ids"]}
    records = list(
        db.scalars(select(Invocation).where(Invocation.id.in_(ids)).order_by(Invocation.id))
    )
    if len(records) != len(ids):
        raise ValueError("Evaluation invocation records are incomplete")
    return {
        "export_schema": SCHEMA,
        "origin": origin,
        "results": evaluation.results,
        "invocations": [
            {
                "id": i.id,
                "model": i.model,
                "status": i.status,
                "latency_ms": i.latency_ms,
                "input_tokens": i.input_tokens,
                "output_tokens": i.output_tokens,
                "cost_usd": i.cost_usd,
                "created_at": i.created_at.isoformat() + "Z",
            }
            for i in records
        ],
    }


def import_snapshot(db: Session, payload: dict) -> int:
    """Idempotently copy demo evaluation/usage only, remapping IDs to avoid local collisions."""
    if not settings().demo_mode:
        raise ValueError("Evaluation import requires DEMO_MODE")
    if payload.get("export_schema") != SCHEMA:
        raise ValueError("Unsupported evaluation snapshot")
    result = copy.deepcopy(payload["results"])
    if result.get("status") != "COMPLETED" or result["cases_run"] != len(result["cases"]):
        raise ValueError("Only complete snapshots with all case records may be imported")
    if len(result["cases"]) > 48 or len(payload["invocations"]) > 240:
        raise ValueError("Snapshot exceeds bounded evaluation limits")
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    for existing in db.scalars(select(Evaluation)):
        if existing.results.get("sync_fingerprint") == fingerprint:
            return existing.id
    mapping = {}
    for row in payload["invocations"]:
        if row["id"] in mapping or Decimal(row["cost_usd"]) < 0:
            raise ValueError("Invalid snapshot invocation")
        values = {
            key: row[key]
            for key in (
                "model",
                "status",
                "latency_ms",
                "input_tokens",
                "output_tokens",
                "cost_usd",
            )
        }
        if any(
            not isinstance(values[k], int) or values[k] < 0
            for k in ("latency_ms", "input_tokens", "output_tokens")
        ):
            raise ValueError("Usage must contain nonnegative integer counters")
        invocation = Invocation(
            case_id=None,
            **values,
            created_at=datetime.fromisoformat(row["created_at"].removesuffix("Z")),
        )
        db.add(invocation)
        db.flush()
        mapping[row["id"]] = invocation.id
    for case in result["cases"]:
        case["source_invocation_ids"] = case["invocation_ids"]
        case["invocation_ids"] = [mapping[i] for i in case["invocation_ids"]]
    # Keep failures in sync with remapped canonical case records.
    result["failures"] = [
        c
        for c in result["cases"]
        if not c["accepted"] or (result["mode"] == "LIVE" and not c["correct"])
    ]
    result["source_evaluation_id"] = result["evaluation_id"]
    result["sync_origin"] = payload["origin"]
    result["sync_fingerprint"] = fingerprint
    evaluation = Evaluation(mode=result["mode"], results={})
    db.add(evaluation)
    db.flush()
    result["evaluation_id"] = evaluation.id
    evaluation.results = result
    return evaluation.id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export")
    export.add_argument("--id", required=True, type=int)
    export.add_argument("--origin", required=True)
    sub.add_parser("import", help="Read trusted synthetic evaluation JSON from stdin; no inference")
    args = parser.parse_args()
    with SessionLocal.begin() as db:
        if args.command == "export":
            print(json.dumps(export_snapshot(db, args.id, args.origin), indent=2))
        else:
            print(
                f"Imported evaluation #{import_snapshot(db, json.load(sys.stdin))}; no model calls."
            )


if __name__ == "__main__":
    main()
