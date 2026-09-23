import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.job_description import JobDescriptionStatus


class JobDescriptionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    raw_text: str = Field(min_length=1)


class EvaluationCriteriaResponse(BaseModel):
    category: str
    weight: float
    version: int

    model_config = {"from_attributes": True}


class JobDescriptionResponse(BaseModel):
    id: uuid.UUID
    title: str
    raw_text: str
    structured_requirements: dict
    status: JobDescriptionStatus
    created_by: uuid.UUID
    created_at: datetime
    criteria: list[EvaluationCriteriaResponse] = []

    model_config = {"from_attributes": True}
