import json
import uuid
from functools import lru_cache
from typing import Any

import boto3

from app.config import get_settings


@lru_cache
def _client():
    settings = get_settings()
    return boto3.client(
        "sqs",
        region_name=settings.aws_region,
        endpoint_url=settings.aws_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def send_evaluation_job(candidate_id: uuid.UUID, jd_id: uuid.UUID) -> None:
    settings = get_settings()
    _client().send_message(
        QueueUrl=settings.sqs_queue_url,
        MessageBody=json.dumps({"candidate_id": str(candidate_id), "jd_id": str(jd_id)}),
    )


def receive_jobs(max_messages: int = 5, wait_seconds: int = 10) -> list[dict[str, Any]]:
    settings = get_settings()
    response = _client().receive_message(
        QueueUrl=settings.sqs_queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=wait_seconds,
    )
    return response.get("Messages", [])


def delete_job(receipt_handle: str) -> None:
    settings = get_settings()
    _client().delete_message(QueueUrl=settings.sqs_queue_url, ReceiptHandle=receipt_handle)
