"""Evaluation Worker — the dedicated worker service consuming the SQS
evaluation-job queue. Deployed as its own ECS Fargate service, independent
of API traffic (see docs/architecture/diagrams/aws_deployment.png).

Run locally with:
    uv run python -m app.workers.evaluation_worker
"""

import json
import logging
import uuid

from app.clients import sqs_client
from app.db import SessionLocal
from app.services import evaluation_service

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_forever() -> None:
    logger.info("Evaluation worker started, polling SQS...")
    while True:
        messages = sqs_client.receive_jobs()
        for message in messages:
            _handle_message(message)


def _handle_message(message: dict) -> None:
    body = json.loads(message["Body"])
    candidate_id = uuid.UUID(body["candidate_id"])
    jd_id = uuid.UUID(body["jd_id"])

    db = SessionLocal()
    try:
        evaluation_service.process_candidate(db, candidate_id, jd_id)
        sqs_client.delete_job(message["ReceiptHandle"])
    except Exception:
        # Leave the message on the queue — it becomes visible again after the
        # visibility timeout and is redriven to a DLQ once a redrive policy
        # (infra, not yet provisioned) is attached to the queue.
        logger.exception("Failed to process candidate %s, leaving message for retry", candidate_id)
    finally:
        db.close()


if __name__ == "__main__":
    run_forever()
