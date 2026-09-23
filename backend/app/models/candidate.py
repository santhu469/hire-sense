import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class DecisionStatus(str, enum.Enum):
    SHORTLISTED = "shortlisted"
    HOLD = "hold"
    REJECTED = "rejected"


class ProcessingStatus(str, enum.Enum):
    """System-driven ingestion/evaluation pipeline state.

    Deliberately separate from `current_status` (the human hiring decision):
    the evaluation worker is only ever allowed to write this column, never
    `current_status`, so "AI never finalizes a hiring decision" is a schema
    fact rather than a convention someone can forget in a new code path.
    """

    PENDING = "pending"
    PARSING = "parsing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class Candidate(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "candidates"

    jd_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"), nullable=False, index=True)
    resume_file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_profile: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    current_status: Mapped[DecisionStatus | None] = mapped_column(
        Enum(DecisionStatus, name="decision_status"), nullable=True
    )
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status"),
        nullable=False,
        default=ProcessingStatus.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
