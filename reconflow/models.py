"""Persistent financial provenance, review, automation and audit entities."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from reconflow.db import Base, now


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(20))


class LoginSession(Base):
    __tablename__ = "login_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class Control(Base):
    __tablename__ = "controls"
    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    worker_heartbeat: Mapped[datetime | None] = mapped_column(DateTime)
    audit_head: Mapped[str] = mapped_column(String(64), default="0" * 64)


class Provider(Base):
    __tablename__ = "providers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    fee_bps: Mapped[int] = mapped_column(Integer, default=200)
    tolerance: Mapped[int] = mapped_column(BigInteger, default=0)
    policy_version: Mapped[str] = mapped_column(String(30), default="net-v1")


class ImportBatch(Base):
    __tablename__ = "imports"
    id: Mapped[int] = mapped_column(primary_key=True)
    digest: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    raw_csv: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="READY")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Payout(Base):
    __tablename__ = "payouts"
    __table_args__ = (UniqueConstraint("provider_id", "external_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    import_id: Mapped[int] = mapped_column(ForeignKey("imports.id"))
    external_id: Mapped[str] = mapped_column(String(100))
    currency: Mapped[str] = mapped_column(String(3))
    account: Mapped[str] = mapped_column(String(40))
    fee: Mapped[int] = mapped_column(BigInteger)
    adjustment: Mapped[int] = mapped_column(BigInteger, default=0)
    declared_net: Mapped[int] = mapped_column(BigInteger)
    settled_at: Mapped[datetime] = mapped_column(DateTime)


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("provider_id", "external_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    payout_id: Mapped[int] = mapped_column(ForeignKey("payouts.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(100))
    amount: Mapped[int] = mapped_column(BigInteger)
    refund: Mapped[int] = mapped_column(BigInteger, default=0)


class BankCredit(Base):
    __tablename__ = "bank_credits"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True)
    import_id: Mapped[int] = mapped_column(ForeignKey("imports.id"))
    reference: Mapped[str] = mapped_column(String(100), index=True)
    account: Mapped[str] = mapped_column(String(40))
    currency: Mapped[str] = mapped_column(String(3))
    amount: Mapped[int] = mapped_column(BigInteger)
    booked_at: Mapped[datetime] = mapped_column(DateTime)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    import_id: Mapped[int] = mapped_column(ForeignKey("imports.id"), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED")
    rule_version: Mapped[str] = mapped_column(String(30), default="net-v1")
    elapsed_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    payout_id: Mapped[int] = mapped_column(ForeignKey("payouts.id"), unique=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    credit_id: Mapped[int | None] = mapped_column(ForeignKey("bank_credits.id"), unique=True)
    expected: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(30))
    rationale: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSON)


class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(primary_key=True)
    payout_id: Mapped[int] = mapped_column(ForeignKey("payouts.id"), unique=True)
    classification: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)


class Investigation(Base):
    __tablename__ = "investigations"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), unique=True)
    mode: Mapped[str] = mapped_column(String(30))
    report: Mapped[dict] = mapped_column(JSON)
    trace: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Proposal(Base):
    __tablename__ = "proposals"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    maker_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    checker_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(30))
    key: Mapped[str] = mapped_column(String(100), unique=True)
    payload: Mapped[dict] = mapped_column(JSON)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    leased_until: Mapped[datetime | None] = mapped_column(DateTime)
    error: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Audit(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(60))
    entity: Mapped[str] = mapped_column(String(100))
    details: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    previous_hash: Mapped[str] = mapped_column(String(64))
    event_hash: Mapped[str] = mapped_column(String(64))


class Invocation(Base):
    __tablename__ = "model_invocations"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int | None] = mapped_column(ForeignKey("cases.id"))
    model: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))
    latency_ms: Mapped[int] = mapped_column(Integer)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[str] = mapped_column(String(30), default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[int] = mapped_column(primary_key=True)
    mode: Mapped[str] = mapped_column(String(30))
    results: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    bucket: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
