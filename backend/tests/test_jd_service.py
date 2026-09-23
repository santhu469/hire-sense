from app.services import jd_service


def test_create_job_description_seeds_default_criteria(db, user):
    jd = jd_service.create_job_description(db, "Senior Backend Engineer", "We need...", user)

    criteria = jd_service.get_current_criteria(db, jd.id)
    categories = {c.category for c in criteria}

    assert categories == {c for c, _ in jd_service.DEFAULT_CRITERIA}
    assert sum(c.weight for c in criteria) == 100.0
    assert all(c.version == 1 for c in criteria)


def test_get_job_description_round_trip(db, user):
    jd = jd_service.create_job_description(db, "Data Analyst", "Some JD text", user)
    fetched = jd_service.get_job_description(db, jd.id)
    assert fetched is not None
    assert fetched.title == "Data Analyst"
