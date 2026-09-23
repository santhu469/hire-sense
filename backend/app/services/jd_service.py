import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evaluation_criteria import EvaluationCriteria
from app.models.job_description import JobDescription
from app.models.user import User

# Default weighted rubric seeded for every new JD. Stored as DB rows (not a
# prompt constant) so weights are configurable per JD even though Phase 1
# has no UI yet to edit them — see EvaluationCriteria.
DEFAULT_CRITERIA: list[tuple[str, float]] = [
    ("Skills Match", 40.0),
    ("Domain Experience", 30.0),
    ("Education & Certifications", 15.0),
    ("Overall Fit", 15.0),
]


def create_job_description(db: Session, title: str, raw_text: str, created_by: User) -> JobDescription:
    jd = JobDescription(title=title, raw_text=raw_text, structured_requirements={}, created_by=created_by.id)
    db.add(jd)
    db.flush()  # assign jd.id without committing yet

    for category, weight in DEFAULT_CRITERIA:
        db.add(EvaluationCriteria(jd_id=jd.id, category=category, weight=weight, version=1))

    db.commit()
    db.refresh(jd)
    return jd


def get_job_description(db: Session, jd_id: uuid.UUID) -> JobDescription | None:
    return db.get(JobDescription, jd_id)


def list_job_descriptions(db: Session) -> list[JobDescription]:
    return list(db.scalars(select(JobDescription).order_by(JobDescription.created_at.desc())))


def get_current_criteria(db: Session, jd_id: uuid.UUID) -> list[EvaluationCriteria]:
    latest_version = db.scalar(
        select(EvaluationCriteria.version)
        .where(EvaluationCriteria.jd_id == jd_id)
        .order_by(EvaluationCriteria.version.desc())
        .limit(1)
    )
    if latest_version is None:
        return []
    return list(
        db.scalars(
            select(EvaluationCriteria).where(
                EvaluationCriteria.jd_id == jd_id, EvaluationCriteria.version == latest_version
            )
        )
    )
