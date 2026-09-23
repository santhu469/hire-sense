import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class EvaluationCriteria(UUIDPrimaryKeyMixin, Base):
    """A weighted scoring category for one JD, one row per (jd, category, version).

    Configurable per JD, never hardcoded into a prompt — rescoring after a
    weight change reads the current version's rows and recomputes the
    weighted sum without a new LLM call.
    """

    __tablename__ = "evaluation_criteria"

    jd_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
