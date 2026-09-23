import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate import Candidate, DecisionStatus
from app.models.evaluation import Evaluation


def list_ranked_candidates(
    db: Session,
    jd_id: uuid.UUID,
    status: DecisionStatus | None = None,
    min_score: float | None = None,
) -> list[tuple[Candidate, Evaluation | None]]:
    """Pure query over Candidate + latest Evaluation. No LLM call on this path."""
    stmt = (
        select(Candidate, Evaluation)
        .outerjoin(Evaluation, (Evaluation.candidate_id == Candidate.id) & (Evaluation.is_latest.is_(True)))
        .where(Candidate.jd_id == jd_id)
    )
    if status is not None:
        stmt = stmt.where(Candidate.current_status == status)
    if min_score is not None:
        stmt = stmt.where(Evaluation.overall_score >= min_score)

    stmt = stmt.order_by(Evaluation.overall_score.desc().nulls_last())
    return list(db.execute(stmt).tuples())
