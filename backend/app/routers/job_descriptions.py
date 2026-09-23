import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.schemas.job_description import JobDescriptionCreateRequest, JobDescriptionResponse
from app.services import jd_service

router = APIRouter(prefix="/job-descriptions", tags=["job-descriptions"])


@router.post("", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    payload: JobDescriptionCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
    jd = jd_service.create_job_description(db, payload.title, payload.raw_text, current_user)
    criteria = jd_service.get_current_criteria(db, jd.id)
    return _to_response(jd, criteria)


@router.get("", response_model=list[JobDescriptionResponse])
def list_job_descriptions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[JobDescriptionResponse]:
    jds = jd_service.list_job_descriptions(db)
    return [_to_response(jd, jd_service.get_current_criteria(db, jd.id)) for jd in jds]


@router.get("/{jd_id}", response_model=JobDescriptionResponse)
def get_job_description(
    jd_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
    jd = jd_service.get_job_description(db, jd_id)
    if jd is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return _to_response(jd, jd_service.get_current_criteria(db, jd_id))


def _to_response(jd, criteria) -> JobDescriptionResponse:
    response = JobDescriptionResponse.model_validate(jd)
    response.criteria = [
        {"category": c.category, "weight": c.weight, "version": c.version} for c in criteria
    ]
    return response
