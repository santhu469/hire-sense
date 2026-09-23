import logging
import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.clients import openai_client, s3_client
from app.models.candidate import Candidate, ProcessingStatus
from app.models.evaluation import Evaluation
from app.services import jd_service
from app.services.resume_parsing import extract_text

logger = logging.getLogger(__name__)


class CandidateNotFoundError(Exception):
    pass


def process_candidate(db: Session, candidate_id: uuid.UUID, jd_id: uuid.UUID) -> Evaluation:
    """The core AI engine — runs as a background job off SQS, never inline in
    an API request. Writes parsed_profile / processing_status / Evaluation
    rows only. It never touches Candidate.current_status or
    CandidateDecision — status changes are decision_service's job alone.
    """
    candidate = db.get(Candidate, candidate_id)
    jd = jd_service.get_job_description(db, jd_id)
    if candidate is None or jd is None:
        raise CandidateNotFoundError(str(candidate_id))

    try:
        candidate.processing_status = ProcessingStatus.PARSING
        db.commit()

        content = s3_client.download_resume(candidate.resume_file_url)
        file_content_type = (
            "application/pdf" if candidate.resume_file_url.lower().endswith(".pdf") else
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        resume_text = extract_text(content, file_content_type)
        candidate.raw_text = resume_text
        db.commit()  # persist extracted text even if the LLM call below fails

        profile = openai_client.extract_candidate_profile(resume_text)
        candidate.parsed_profile = profile.model_dump()
        candidate.processing_status = ProcessingStatus.EVALUATING
        db.commit()

        criteria = jd_service.get_current_criteria(db, jd_id)
        categories = [c.category for c in criteria]
        weights_by_category = {c.category: c.weight for c in criteria}
        criteria_version = criteria[0].version if criteria else 1

        llm_output = openai_client.evaluate_candidate(profile, jd.structured_requirements, categories)

        category_scores = {item.category: item.score for item in llm_output.category_scores}
        total_weight = sum(weights_by_category.values()) or 1.0
        overall_score = sum(
            category_scores.get(category, 0.0) * weight for category, weight in weights_by_category.items()
        ) / total_weight

        db.execute(
            update(Evaluation)
            .where(Evaluation.candidate_id == candidate_id, Evaluation.is_latest.is_(True))
            .values(is_latest=False)
        )
        evaluation = Evaluation(
            candidate_id=candidate.id,
            jd_id=jd_id,
            criteria_version=criteria_version,
            overall_score=overall_score,
            category_scores=category_scores,
            insights=llm_output.insights.model_dump(),
            is_latest=True,
        )
        db.add(evaluation)
        candidate.processing_status = ProcessingStatus.COMPLETED
        db.commit()
        db.refresh(evaluation)
        return evaluation

    except Exception as exc:
        db.rollback()
        candidate = db.get(Candidate, candidate_id)
        candidate.processing_status = ProcessingStatus.FAILED
        candidate.error_message = str(exc)[:2000]
        db.commit()
        logger.exception("Evaluation failed for candidate %s", candidate_id)
        raise


def get_latest_evaluation(db: Session, candidate_id: uuid.UUID) -> Evaluation | None:
    return db.scalar(
        select(Evaluation).where(Evaluation.candidate_id == candidate_id, Evaluation.is_latest.is_(True))
    )
