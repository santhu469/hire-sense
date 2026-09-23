import uuid
from unittest.mock import patch

from app.models.candidate import Candidate, ProcessingStatus
from app.schemas.evaluation import CandidateProfile, CategoryScoreItem, EvaluationInsights, EvaluationLLMOutput
from app.services import evaluation_service, jd_service


def _make_candidate(db, user):
    jd = jd_service.create_job_description(db, "Backend Engineer", "JD text", user)
    candidate = Candidate(id=uuid.uuid4(), jd_id=jd.id, resume_file_url="resumes/fake.pdf")
    db.add(candidate)
    db.flush()
    return candidate, jd


FAKE_PROFILE = CandidateProfile(name="Jane Doe", skills=["Python", "SQL"], experience_years=5)

FAKE_INSIGHTS = EvaluationInsights(
    summary="Strong backend candidate.",
    strengths=["Python"],
    matching_skills=["Python", "SQL"],
    gaps=["No Kubernetes experience"],
    differentiators=["Open source contributions"],
    concerns=[],
    recommendation="Shortlist for interview.",
)

# Default criteria are Skills Match 40 / Domain Experience 30 /
# Education & Certifications 15 / Overall Fit 15 (jd_service.DEFAULT_CRITERIA).
FAKE_LLM_OUTPUT = EvaluationLLMOutput(
    category_scores=[
        CategoryScoreItem(category="Skills Match", score=90.0),
        CategoryScoreItem(category="Domain Experience", score=70.0),
        CategoryScoreItem(category="Education & Certifications", score=60.0),
        CategoryScoreItem(category="Overall Fit", score=80.0),
    ],
    insights=FAKE_INSIGHTS,
)


def test_process_candidate_computes_weighted_score_in_app_code(db, user):
    candidate, jd = _make_candidate(db, user)

    with (
        patch("app.services.evaluation_service.s3_client.download_resume", return_value=b"fake pdf bytes"),
        patch("app.services.evaluation_service.extract_text", return_value="Jane Doe resume text"),
        patch("app.services.evaluation_service.openai_client.extract_candidate_profile", return_value=FAKE_PROFILE) as extract_mock,
        patch("app.services.evaluation_service.openai_client.evaluate_candidate", return_value=FAKE_LLM_OUTPUT) as evaluate_mock,
    ):
        evaluation = evaluation_service.process_candidate(db, candidate.id, jd.id)

    # The LLM call is never asked for (and never returns) a pre-computed total
    # -- only per-category scores + insights. The weighted sum below is
    # computed independently in application code.
    assert "overall_score" not in evaluate_mock.return_value.model_dump()
    expected_overall = (90.0 * 40 + 70.0 * 30 + 60.0 * 15 + 80.0 * 15) / 100
    assert evaluation.overall_score == expected_overall

    assert evaluation.is_latest is True
    assert evaluation.category_scores == {
        "Skills Match": 90.0,
        "Domain Experience": 70.0,
        "Education & Certifications": 60.0,
        "Overall Fit": 80.0,
    }
    assert evaluation.insights["recommendation"] == "Shortlist for interview."

    extract_mock.assert_called_once()
    evaluate_mock.assert_called_once()


def test_process_candidate_never_touches_decision_status(db, user):
    candidate, jd = _make_candidate(db, user)

    with (
        patch("app.services.evaluation_service.s3_client.download_resume", return_value=b"fake pdf bytes"),
        patch("app.services.evaluation_service.extract_text", return_value="Jane Doe resume text"),
        patch("app.services.evaluation_service.openai_client.extract_candidate_profile", return_value=FAKE_PROFILE),
        patch("app.services.evaluation_service.openai_client.evaluate_candidate", return_value=FAKE_LLM_OUTPUT),
    ):
        evaluation_service.process_candidate(db, candidate.id, jd.id)

    db.refresh(candidate)
    assert candidate.current_status is None  # only decision_service may set this
    assert candidate.processing_status == ProcessingStatus.COMPLETED


def test_process_candidate_marks_failed_on_error(db, user):
    candidate, jd = _make_candidate(db, user)

    with patch("app.services.evaluation_service.s3_client.download_resume", side_effect=RuntimeError("S3 down")):
        try:
            evaluation_service.process_candidate(db, candidate.id, jd.id)
        except RuntimeError:
            pass

    db.refresh(candidate)
    assert candidate.processing_status == ProcessingStatus.FAILED
    assert "S3 down" in candidate.error_message
