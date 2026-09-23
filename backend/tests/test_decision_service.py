import uuid

from app.models.candidate import Candidate, DecisionStatus
from app.services import decision_service, jd_service


def _make_candidate(db, user):
    jd = jd_service.create_job_description(db, "QA Engineer", "JD text", user)
    candidate = Candidate(id=uuid.uuid4(), jd_id=jd.id, resume_file_url="resumes/fake.pdf")
    db.add(candidate)
    db.flush()
    return candidate


def test_change_status_inserts_audit_row_and_updates_current_status(db, user):
    candidate = _make_candidate(db, user)
    assert candidate.current_status is None

    decision = decision_service.change_candidate_status(
        db, candidate.id, DecisionStatus.SHORTLISTED, "Strong skills match", user
    )

    assert decision.status == DecisionStatus.SHORTLISTED
    assert decision.changed_by == user.id
    assert candidate.current_status == DecisionStatus.SHORTLISTED


def test_status_changes_are_append_only_not_overwritten(db, user):
    candidate = _make_candidate(db, user)

    first = decision_service.change_candidate_status(db, candidate.id, DecisionStatus.HOLD, None, user)
    second = decision_service.change_candidate_status(db, candidate.id, DecisionStatus.SHORTLISTED, None, user)

    assert first.id != second.id
    assert candidate.current_status == DecisionStatus.SHORTLISTED
