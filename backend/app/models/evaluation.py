import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class Evaluation(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Append-only. Rescoring inserts a new row and flips `is_latest` —
    existing rows are never updated in place, so score history is preserved.
    """

    __tablename__ = "evaluations"

    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    jd_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"), nullable=False, index=True)
    criteria_version: Mapped[int] = mapped_column(Integer, nullable=False)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    # {category: score, ...} — category scores as returned by the LLM.
    category_scores: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # {summary, strengths, matching_skills, gaps, differentiators, concerns,
    #  recommendation} — always present alongside the score, never a bare number.
    insights: Mapped[dict] = mapped_column(JSONB, nullable=False)

    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
