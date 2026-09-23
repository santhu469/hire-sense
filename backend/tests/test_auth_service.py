import pytest

from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.services import auth_service
from app.services.auth_service import EmailAlreadyRegisteredError, InvalidCredentialsError


def test_password_hash_round_trip():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_jwt_round_trip():
    import uuid

    user_id = uuid.uuid4()
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    assert decode_token(access, expected_type="access") == user_id
    assert decode_token(refresh, expected_type="refresh") == user_id

    with pytest.raises(Exception):
        decode_token(access, expected_type="refresh")


def test_register_then_authenticate(db):
    user = auth_service.register_user(db, "new-user@example.com", "hunter2hunter2")
    authenticated = auth_service.authenticate_user(db, "new-user@example.com", "hunter2hunter2")
    assert authenticated.id == user.id

    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate_user(db, "new-user@example.com", "wrong-password")


def test_register_duplicate_email_rejected(db):
    auth_service.register_user(db, "dupe@example.com", "hunter2hunter2")
    with pytest.raises(EmailAlreadyRegisteredError):
        auth_service.register_user(db, "dupe@example.com", "another-password")
