import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models import Base
from app.models.user import User


def _test_database_url() -> str:
    """Same server as dev, but a dedicated `_test` database so the test
    suite never touches dev data or requires dropping real tables."""
    base_url = get_settings().database_url
    root, _, dbname = base_url.rpartition("/")
    return f"{root}/{dbname}_test"


@pytest.fixture(scope="session")
def engine():
    admin_engine = create_engine(get_settings().database_url, isolation_level="AUTOCOMMIT")
    test_url = _test_database_url()
    test_dbname = test_url.rpartition("/")[2]
    with admin_engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{test_dbname}"'))
        conn.execute(text(f'CREATE DATABASE "{test_dbname}"'))
    admin_engine.dispose()

    engine = create_engine(test_url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine) -> Session:
    """A session bound to an outer transaction that's always rolled back,
    even though service-layer code calls session.commit() internally --
    join_transaction_mode="create_savepoint" makes those commits only
    release a SAVEPOINT, keeping the outer transaction (and test isolation)
    intact.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def user(db: Session) -> User:
    user = User(id=uuid.uuid4(), email="recruiter@example.com", password_hash="not-a-real-hash")
    db.add(user)
    db.flush()
    return user
