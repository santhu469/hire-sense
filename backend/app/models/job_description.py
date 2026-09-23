import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class JobDescriptionStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class JobDescription(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "job_descriptions"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Structured requirements (must-have skills, nice-to-have, experience range,
    # responsibilities) produced from raw_text — kept as JSONB so new fields
    # don't require a migration every time extraction improves.
    structured_requirements: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[JobDescriptionStatus] = mapped_column(
        Enum(JobDescriptionStatus, name="job_description_status"),
        nullable=False,
        default=JobDescriptionStatus.ACTIVE,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
