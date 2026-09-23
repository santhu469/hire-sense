from functools import lru_cache

from openai import OpenAI

from app.config import get_settings
from app.schemas.evaluation import CandidateProfile, EvaluationLLMOutput


@lru_cache
def _client() -> OpenAI:
    return OpenAI(api_key=get_settings().openai_api_key)


def extract_candidate_profile(resume_text: str) -> CandidateProfile:
    """Structured extraction of a resume into a CandidateProfile — never free-text parsing."""
    completion = _client().chat.completions.parse(
        model=get_settings().openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract candidate information from the resume text into the given schema. "
                    "Leave fields null/empty if not present in the text. Do not invent information."
                ),
            },
            {"role": "user", "content": resume_text},
        ],
        response_format=CandidateProfile,
    )
    return completion.choices[0].message.parsed


def evaluate_candidate(
    profile: CandidateProfile,
    jd_structured_requirements: dict,
    categories: list[str],
) -> EvaluationLLMOutput:
    """Structured scoring call — returns per-category scores plus explainable
    insights, never a bare number. The weighted overall score is computed
    deterministically in evaluation_service, not by the LLM.
    """
    completion = _client().chat.completions.parse(
        model=get_settings().openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a candidate evaluation assistant. Score the candidate profile "
                    "against the job description requirements, one score from 0 to 100 for "
                    "EACH of the following categories, in this exact set: "
                    f"{', '.join(categories)}. "
                    "Also provide structured insights: a short summary, strengths, matching "
                    "skills, gaps, differentiators, concerns, and a recommendation. Be specific "
                    "and grounded in the candidate profile and JD requirements — never invent "
                    "skills or experience not present in the profile."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Job description requirements:\n{jd_structured_requirements}\n\n"
                    f"Candidate profile:\n{profile.model_dump_json()}"
                ),
            },
        ],
        response_format=EvaluationLLMOutput,
    )
    return completion.choices[0].message.parsed
