import uuid

from sqlalchemy.orm import Session

from app.models.candidate import Candidate, DecisionStatus
from app.models.candidate_decision import CandidateDecision
from app.models.user import User


class CandidateNotFoundError(Exception):
    pass


def change_candidate_status(
    db: Session,
    candidate_id: uuid.UUID,
    new_status: DecisionStatus,
    reason_note: str | None,
    changed_by: User,
) -> CandidateDecision:
    """The only code path allowed to write Candidate.current_status.

    Always a human-initiated, authenticated call — never invoked from the
    evaluation worker. CandidateDecision is append-only: this inserts a new
    row rather than mutating a prior one, preserving decision history.
    """
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise CandidateNotFoundError(str(candidate_id))

    decision = CandidateDecision(
        candidate_id=candidate.id,
        jd_id=candidate.jd_id,
        status=new_status,
        changed_by=changed_by.id,
        reason_note=reason_note,
    )
    db.add(decision)
    candidate.current_status = new_status
    db.commit()
    db.refresh(decision)
    return decision
