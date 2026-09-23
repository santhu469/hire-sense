import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

import bcrypt
import jwt

from app.config import get_settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_token(user_id: uuid.UUID, token_type: Literal["access", "refresh"], ttl: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "exp": now + ttl,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def create_access_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    return _create_token(user_id, "access", timedelta(minutes=settings.jwt_access_ttl_minutes))


def create_refresh_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    return _create_token(user_id, "refresh", timedelta(days=settings.jwt_refresh_ttl_days))


class InvalidTokenError(Exception):
    pass


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> uuid.UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"expected a {expected_type} token")

    return uuid.UUID(payload["sub"])
