"""Non-destructive PostgreSQL checks in a temporary schema, intended inside app container."""

import hashlib
import json
import secrets

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from reconflow.config import settings
from reconflow.db import Base
from reconflow.models import Audit, Control, Job, Provider, User
from reconflow.services.audit import append

engine = create_engine(settings().database_url)
schema = "check_" + secrets.token_hex(8)
with engine.begin() as conn:
    conn.execute(text(f'CREATE SCHEMA "{schema}"'))
try:
    with engine.begin() as conn:
        conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        Base.metadata.create_all(conn)
        with Session(bind=conn) as db:
            db.add(Control(id=1))
            db.add(Provider(name="SyntheticPay", fee_bps=200, tolerance=0))
            db.add(User(id=1, email="check@synthetic.demo", role="analyst", password_hash="unused"))
            db.flush()
            db.add(Job(kind="check", key="claim-one", actor_id=1, payload={}))
            db.flush()
    with engine.connect() as one, engine.connect() as two:
        with one.begin(), two.begin():
            one.execute(text(f'SET LOCAL search_path TO "{schema}"'))
            two.execute(text(f'SET LOCAL search_path TO "{schema}"'))
            query = select(Job).where(Job.status == "PENDING").with_for_update(skip_locked=True)
            assert one.execute(query).first() is not None
            assert two.execute(query).first() is None
    with engine.begin() as conn:
        conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        with Session(bind=conn) as db:
            append(db, "check", "first", "entity", value=1)
            append(db, "check", "second", "entity", value=2)
            db.flush()
            head = "0" * 64
            for row in db.scalars(select(Audit).order_by(Audit.id)):
                assert row.previous_hash == head
                body = json.dumps(
                    [row.actor, row.action, row.entity, row.details, row.created_at.isoformat()],
                    sort_keys=True,
                )
                head = hashlib.sha256((head + body).encode()).hexdigest()
                assert row.event_hash == head
            assert db.get(Control, 1).audit_head == head
    # Existing deployed audit table must reject SQL UPDATE, even from application role.
    from sqlalchemy.exc import DBAPIError

    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE public.audit_events SET action='tampered' "
                    "WHERE id=(SELECT min(id) FROM public.audit_events)"
                )
            )
    except DBAPIError:
        print("PASS: deployed audit UPDATE denied")
    else:
        raise AssertionError("Audit mutation guard missing")
    print("PASS: PostgreSQL competing SKIP LOCKED claims and hash-chain verification")
finally:
    with engine.begin() as conn:
        conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
