import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.clients import s3_client, sqs_client
from app.models.candidate import Candidate

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class UnsupportedFileTypeError(Exception):
    pass


def create_candidate_from_upload(db: Session, jd_id: uuid.UUID, file: UploadFile) -> Candidate:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedFileTypeError(file.content_type)

    candidate_id = uuid.uuid4()
    key = f"resumes/{jd_id}/{candidate_id}/{file.filename}"
    content = file.file.read()
    s3_client.upload_resume(key=key, content=content, content_type=file.content_type)

    candidate = Candidate(id=candidate_id, jd_id=jd_id, resume_file_url=key)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    sqs_client.send_evaluation_job(candidate_id=candidate.id, jd_id=jd_id)
    return candidate
