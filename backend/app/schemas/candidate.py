import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.candidate import DecisionStatus, ProcessingStatus
from app.schemas.evaluation import EvaluationResponse


class CandidateUploadResponse(BaseModel):
    id: uuid.UUID
    jd_id: uuid.UUID
    processing_status: ProcessingStatus
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class CandidateResponse(BaseModel):
    id: uuid.UUID
    jd_id: uuid.UUID
    current_status: DecisionStatus | None
    processing_status: ProcessingStatus
    error_message: str | None
    parsed_profile: dict | None
    uploaded_at: datetime
    latest_evaluation: EvaluationResponse | None = None

    model_config = {"from_attributes": True}


class StatusChangeRequest(BaseModel):
    status: DecisionStatus
    reason_note: str | None = Field(default=None, max_length=2000)
