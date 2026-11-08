"""Human case state transitions and dual control at the service boundary."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from reconflow.db import now
from reconflow.models import Case, Control, Investigation, Job, Proposal, User
from reconflow.services.audit import append


def propose(db: Session, case_id: int, actor: User, note: str) -> Proposal:
    if actor.role not in ("analyst", "supervisor"):
        raise PermissionError("Only analysts or supervisors may propose")
    db.scalar(
        select(Control)
        .where(Control.id == 1)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    case = db.scalar(
        select(Case)
        .where(Case.id == case_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if not case or case.status not in ("OPEN", "INVESTIGATING", "ESCALATED"):
        raise ValueError("Case cannot accept a proposal in its current state")
    if not 10 <= len(note.strip()) <= 2000:
        raise ValueError("Provide a 10–2000 character evidence-based recommendation")
    proposal = Proposal(case_id=case_id, maker_id=actor.id, note=note.strip())
    db.add(proposal)
    case.status = "NEEDS_REVIEW"
    append(db, actor.id, "review.proposed", f"case:{case_id}")
    return proposal


def decide(db: Session, proposal_id: int, actor: User, decision: str) -> None:
    if actor.role != "supervisor":
        raise PermissionError("Supervisor required")
    # Same Control -> Case order as worker/audit; fence a concurrent report/decision.
    db.scalar(
        select(Control)
        .where(Control.id == 1)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    candidate = db.get(Proposal, proposal_id)
    if not candidate:
        raise ValueError("Proposal unavailable")
    case = db.scalar(
        select(Case)
        .where(Case.id == candidate.case_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    proposal = db.scalar(
        select(Proposal)
        .where(Proposal.id == proposal_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if not proposal or proposal.status != "PENDING":
        raise ValueError("Proposal no longer pending")
    if proposal.maker_id == actor.id:
        raise PermissionError("Maker cannot approve or reject own proposal")
    if decision not in ("APPROVED", "REJECTED", "ESCALATED"):
        raise ValueError("Invalid decision")
    if case.status != "NEEDS_REVIEW":
        raise ValueError("Case is no longer awaiting this decision")
    if decision == "APPROVED":
        reason = approval_block_reason(db, case.id)
        if reason:
            raise ValueError(reason)
    proposal.status, proposal.checker_id, proposal.decided_at = decision, actor.id, now()
    case.status = {"APPROVED": "RESOLVED", "REJECTED": "OPEN", "ESCALATED": "ESCALATED"}[decision]
    case.resolved_at = now() if decision == "APPROVED" else None
    append(db, actor.id, "review." + decision.lower(), f"case:{case.id}", proposal=proposal.id)


def approval_block_reason(db: Session, case_id: int) -> str | None:
    """Read-only UI hint; decide rechecks under locks, so the browser is never the policy gate."""
    query = select(Job).where(Job.kind == "investigate", Job.key.like(f"ai:{case_id}:%"))
    if db.scalar(query.where(Job.status.in_(["PENDING", "LEASED", "RETRY_WAIT"]))):
        return "Investigation is pending; reject or escalate instead"
    latest_job = db.scalar(query.order_by(Job.id.desc()).limit(1))
    latest = db.scalar(
        select(Investigation)
        .where(Investigation.case_id == case_id)
        .order_by(Investigation.id.desc())
        .limit(1)
    )
    if latest_job and (
        latest_job.status != "COMPLETED" or not latest or latest.job_id != latest_job.id
    ):
        return "Latest investigation has no completed report; reject or escalate"
    if latest and latest.mode in ("LIVE_FAILED_FALLBACK", "LIVE_REVIEW_REQUIRED"):
        return "Unsupported AI output requires escalation or rejection"
    if latest and latest.report.get("version") == "controlled-investigator-v2":
        report = latest.report
        if not report.get("validation", {}).get("consistent", False) or report.get(
            "assessment", {}
        ).get("must_escalate", True):
            return "Unsupported or incomplete AI findings require escalation or rejection"
    return None
