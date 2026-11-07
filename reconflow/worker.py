"""One DB-leased worker; handlers commit atomically with completion and retain row lock."""

import time
from datetime import timedelta

from sqlalchemy import and_, or_, select

from reconflow.db import SessionLocal, now
from reconflow.models import Control, Job
from reconflow.services.ai import investigate
from reconflow.services.audit import append
from reconflow.services.reconciliation import reconcile


def tick() -> bool:
    """Claim/recover one job with SKIP LOCKED. Handler lock fences expired leases."""
    with SessionLocal.begin() as db:
        control = db.get(Control, 1)
        if control:
            control.worker_heartbeat = now()
        job = db.scalar(
            select(Job)
            .where(
                or_(
                    and_(Job.status.in_(["PENDING", "RETRY_WAIT"]), Job.available_at <= now()),
                    and_(Job.status == "LEASED", Job.leased_until < now()),
                )
            )
            .order_by(Job.id)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if not job:
            return False
        if job.attempts >= 3:
            job.status, job.error, job.leased_until = "DEAD_LETTER", "LEASE_RECOVERY_LIMIT", None
            append(db, "worker", "job.dead_lettered", f"job:{job.id}", attempts=job.attempts)
            return True
        job.status, job.leased_until = "LEASED", now() + timedelta(seconds=180)
        job.attempts += 1
        job_id, attempt = job.id, job.attempts
    try:
        with SessionLocal.begin() as db:
            job = db.scalar(select(Job).where(Job.id == job_id).with_for_update())
            if job.status != "LEASED" or job.attempts != attempt:
                return True
            if job.payload.get("fail_once") and attempt == 1:
                raise RuntimeError("INJECTED_FAILURE")
            if job.kind == "reconcile":
                reconcile(db, job.payload["run_id"], job.actor_id)
            elif job.kind == "investigate":
                investigate(db, job)
            else:
                raise ValueError("Unknown job kind")
            job.status, job.error, job.leased_until = "COMPLETED", None, None
            append(db, job.actor_id, "job.completed", f"job:{job.id}", attempts=attempt)
    except Exception as exc:
        with SessionLocal.begin() as db:
            job = db.scalar(select(Job).where(Job.id == job_id).with_for_update())
            if job.attempts == attempt and job.status == "LEASED":
                job.status = "DEAD_LETTER" if attempt >= 3 else "RETRY_WAIT"
                job.available_at = now() + timedelta(seconds=2**attempt)
                job.leased_until = None
                job.error = (
                    "INJECTED_FAILURE" if str(exc) == "INJECTED_FAILURE" else type(exc).__name__
                )
                append(
                    db,
                    "worker",
                    "job.failed",
                    f"job:{job.id}",
                    error=job.error,
                    attempt=attempt,
                    status=job.status,
                )
    return True


def main() -> None:
    while True:
        try:
            busy = tick()
        except Exception as exc:
            print(f"Worker database error: {type(exc).__name__}", flush=True)
            busy = False
        if not busy:
            time.sleep(1)


if __name__ == "__main__":
    main()
