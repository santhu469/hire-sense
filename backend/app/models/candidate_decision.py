import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.candidate import DecisionStatus


class CandidateDecision(UUIDPrimaryKeyMixin, Base):
    """Append-only audit log. This table, plus `changed_by`, is what makes a
    status change traceable to a specific authenticated human action — the
    only way `Candidate.current_status` is allowed to change.
    """

    __tablename__ = "candidate_decisions"

    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    jd_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"), nullable=False, index=True)
    status: Mapped[DecisionStatus] = mapped_column(Enum(DecisionStatus, name="decision_status"), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
