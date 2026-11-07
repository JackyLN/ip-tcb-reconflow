"""Serialized append-only application audit chain (DB owner can still tamper)."""

import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from reconflow.db import now
from reconflow.models import Audit, Control


def append(db: Session, actor: str | int, action: str, entity: str, **details: object) -> None:
    control = db.scalar(
        select(Control)
        .where(Control.id == 1)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if control is None:
        control = Control(id=1, audit_head="0" * 64)
        db.add(control)
        db.flush()
    stamp = now()
    body = json.dumps([str(actor), action, entity, details, stamp.isoformat()], sort_keys=True)
    digest = hashlib.sha256((control.audit_head + body).encode()).hexdigest()
    db.add(
        Audit(
            actor=str(actor),
            action=action,
            entity=entity,
            details=details,
            created_at=stamp,
            previous_hash=control.audit_head,
            event_hash=digest,
        )
    )
    control.audit_head = digest
