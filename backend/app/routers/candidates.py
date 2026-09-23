import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.candidate import Candidate, DecisionStatus
from app.schemas.candidate import CandidateResponse, CandidateUploadResponse, StatusChangeRequest
from app.services import decision_service, evaluation_service, ingestion_service, ranking_service
from app.services.decision_service import CandidateNotFoundError
from app.services.ingestion_service import UnsupportedFileTypeError

router = APIRouter(tags=["candidates"])


@router.post(
    "/job-descriptions/{jd_id}/candidates",
    response_model=CandidateUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def upload_candidate(
    jd_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateUploadResponse:
    try:
        candidate = ingestion_service.create_candidate_from_upload(db, jd_id, file)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX resumes are supported",
        ) from exc

    return CandidateUploadResponse.model_validate(candidate)


@router.get("/job-descriptions/{jd_id}/candidates", response_model=list[CandidateResponse])
def list_ranked_candidates(
    jd_id: uuid.UUID,
    status_filter: DecisionStatus | None = None,
    min_score: float | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CandidateResponse]:
    rows = ranking_service.list_ranked_candidates(db, jd_id, status=status_filter, min_score=min_score)
    return [_to_response(candidate, evaluation) for candidate, evaluation in rows]


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateResponse:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    evaluation = evaluation_service.get_latest_evaluation(db, candidate_id)
    return _to_response(candidate, evaluation)


@router.patch("/candidates/{candidate_id}/status", response_model=CandidateResponse)
def change_status(
    candidate_id: uuid.UUID,
    payload: StatusChangeRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateResponse:
    """The only endpoint that can change a candidate's hiring decision status.
    Always a human-initiated, authenticated call — never invoked by the
    evaluation worker."""
    try:
        decision_service.change_candidate_status(db, candidate_id, payload.status, payload.reason_note, current_user)
    except CandidateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found") from exc

    candidate = db.get(Candidate, candidate_id)
    evaluation = evaluation_service.get_latest_evaluation(db, candidate_id)
    return _to_response(candidate, evaluation)


def _to_response(candidate, evaluation) -> CandidateResponse:
    response = CandidateResponse.model_validate(candidate)
    if evaluation is not None:
        response.latest_evaluation = evaluation
    return response
