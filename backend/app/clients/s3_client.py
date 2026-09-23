from functools import lru_cache

import boto3

from app.config import get_settings


@lru_cache
def _client():
    settings = get_settings()
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        endpoint_url=settings.aws_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def upload_resume(key: str, content: bytes, content_type: str) -> str:
    settings = get_settings()
    _client().put_object(Bucket=settings.s3_bucket_name, Key=key, Body=content, ContentType=content_type)
    return key


def download_resume(key: str) -> bytes:
    settings = get_settings()
    obj = _client().get_object(Bucket=settings.s3_bucket_name, Key=key)
    return obj["Body"].read()
