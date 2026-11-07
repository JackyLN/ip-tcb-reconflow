"""Measured isolated synthetic processing benchmark. No human productivity claims."""

import json
import platform
import secrets
from time import perf_counter

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from reconflow.config import settings
from reconflow.db import Base
from reconflow.models import Control, Provider, Run, User
from reconflow.services.ingestion import ingest, scenario_csv
from reconflow.services.reconciliation import reconcile

engine = create_engine(settings().database_url)
schema = "bench_" + secrets.token_hex(8)
results = []
with engine.begin() as conn:
    conn.execute(text(f'CREATE SCHEMA "{schema}"'))
try:
    with engine.begin() as conn:
        conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        Base.metadata.create_all(conn)
        with Session(bind=conn) as db:
            db.add_all(
                [
                    Control(id=1),
                    Provider(name="SyntheticPay", fee_bps=200, tolerance=0),
                    User(
                        id=1, email="bench@synthetic.demo", role="analyst", password_hash="unused"
                    ),
                ]
            )
            db.flush()
            for size in (100, 1000, 10000):
                raw = scenario_csv(size, "mismatch")
                start = perf_counter()
                source = ingest(db, raw, "Synthetic benchmark", 1)
                db.flush()
                ingest_ms = int((perf_counter() - start) * 1000)
                run = db.scalar(select(Run).where(Run.import_id == source.id))
                reconcile(db, run.id, 1)
                db.flush()
                results.append(
                    {
                        "payments": size,
                        "payouts": size // 20,
                        "import_ms": ingest_ms,
                        "reconcile_ms": run.elapsed_ms,
                    }
                )
    print(
        json.dumps(
            {
                "label": "MEASURED synthetic local Docker, single sample, not a bank benchmark",
                "architecture": platform.machine(),
                "runtime": platform.python_version(),
                "container_limits": "1 CPU / 512 MB",
                "records": results,
            },
            indent=2,
        )
    )
finally:
    with engine.begin() as conn:
        conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
