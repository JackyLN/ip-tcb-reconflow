"""Human case state transitions and dual control at the service boundary."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from reconflow.db import now
from reconflow.models import Case, Proposal, User
from reconflow.services.audit import append


def propose(db: Session, case_id: int, actor: User, note: str) -> Proposal:
    if actor.role not in ("analyst", "supervisor"):
        raise PermissionError("Only analysts or supervisors may propose")
    case = db.scalar(select(Case).where(Case.id == case_id).with_for_update())
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
    proposal = db.scalar(select(Proposal).where(Proposal.id == proposal_id).with_for_update())
    if not proposal or proposal.status != "PENDING":
        raise ValueError("Proposal no longer pending")
    if proposal.maker_id == actor.id:
        raise PermissionError("Maker cannot approve or reject own proposal")
    if decision not in ("APPROVED", "REJECTED", "ESCALATED"):
        raise ValueError("Invalid decision")
    case = db.scalar(select(Case).where(Case.id == proposal.case_id).with_for_update())
    proposal.status, proposal.checker_id, proposal.decided_at = decision, actor.id, now()
    case.status = {"APPROVED": "RESOLVED", "REJECTED": "OPEN", "ESCALATED": "ESCALATED"}[decision]
    case.resolved_at = now() if decision == "APPROVED" else None
    append(db, actor.id, "review." + decision.lower(), f"case:{case.id}", proposal=proposal.id)
