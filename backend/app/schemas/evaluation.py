import uuid
from datetime import datetime

from pydantic import BaseModel


class EvaluationInsights(BaseModel):
    """Structured explanation that must accompany every score — never a bare number."""

    summary: str
    strengths: list[str]
    matching_skills: list[str]
    gaps: list[str]
    differentiators: list[str]
    concerns: list[str]
    recommendation: str


class CandidateProfile(BaseModel):
    """Structured extraction of a resume — the LLM's ingestion-time output."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = []
    experience_years: float | None = None
    experience_timeline: list[str] = []
    education: list[str] = []
    certifications: list[str] = []


class CategoryScoreItem(BaseModel):
    category: str
    score: float  # 0-100


class EvaluationLLMOutput(BaseModel):
    """Exact shape requested from the OpenAI structured-output call.

    Category scores are a list, not a dict: JSON Schema strict mode requires
    a fixed property set, but the category set is configurable per JD
    (EvaluationCriteria), so a dict with per-JD keys can't be a strict schema.
    evaluation_service converts this list to a dict before persisting.
    """

    category_scores: list[CategoryScoreItem]
    insights: EvaluationInsights


class EvaluationResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    jd_id: uuid.UUID
    criteria_version: int
    overall_score: float
    category_scores: dict[str, float]
    insights: EvaluationInsights
    is_latest: bool
    created_at: datetime

    model_config = {"from_attributes": True}
