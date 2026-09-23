from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(db: Session, email: str, password: str) -> User:
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise EmailAlreadyRegisteredError(email)

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError(email)
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    return create_access_token(user.id), create_refresh_token(user.id)


def refresh_access_token(db: Session, refresh_token: str) -> str:
    user_id = decode_token(refresh_token, expected_type="refresh")
    user = db.get(User, user_id)
    if user is None:
        raise InvalidCredentialsError(str(user_id))
    return create_access_token(user.id)
