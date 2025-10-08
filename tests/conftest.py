# ruff: no-format
# ruff: noqa: E402

# DONT FORMAT THIS FILE - it breaks sys.path manipulation
import contextlib
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

for p in (PROJECT_ROOT, SRC_DIR):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

# End sys path manipulation

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from src.budgetbuddy.api.app import app
from src.budgetbuddy.api.deps import get_db
from src.db.schema.base import DEFAULT_SCHEMA, Base

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

# Insert at the front so it takes precedence over site-packages
for p in (PROJECT_ROOT, SRC_DIR):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests that don't require database or external services")
    config.addinivalue_line("markers", "integration: Integration tests that use database")
    config.addinivalue_line("markers", "smoke: Quick smoke tests for CI/CD")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres_TEST_:postgres@localhost:5432/budgetbuddy_test",
)


@pytest.fixture(scope="session")
def test_engine():
    """Create a SQLAlchemy engine for tests.

    If USE_TESTCONTAINERS is set, spin up an ephemeral Postgres.
    Otherwise, connect to TEST_DATABASE_URL. Ensures schema and tables exist.
    If DB is not reachable, gracefully skip DB-dependent tests.
    """
    use_tc = os.getenv("USE_TESTCONTAINERS")
    if use_tc:
        try:
            from testcontainers.postgres import PostgresContainer
        except Exception as exc:
            pytest.skip(f"USE_TESTCONTAINERS set, but testcontainers is unavailable: {exc}")
        container = PostgresContainer("postgres:16-alpine")
        container.start()
        url = container.get_connection_url()
        engine = create_engine(url, pool_pre_ping=True)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            with engine.begin() as conn:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DEFAULT_SCHEMA}"))
            Base.metadata.create_all(bind=engine)
            yield engine
        finally:
            Base.metadata.drop_all(bind=engine)
            with contextlib.suppress(Exception):
                container.stop()
        return

    # Fallback to TEST_DATABASE_URL path
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

    # Check connectivity; if fails, skip all tests that depend on the engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as exc:
        pytest.skip(
            f"Skipping DB tests: cannot connect to TEST_DATABASE_URL, \
            Set TEST_DATABASE_URL or start Postgres. Details: {exc}",
        )

    # Ensure schema exists and create tables from metadata
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DEFAULT_SCHEMA}"))
    Base.metadata.create_all(bind=engine)

    yield engine

    # Optional teardown: drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(test_engine):
    """Provide a database session that uses nested transactions (SAVEPOINT) per test.

    Pattern:
    - Open a connection and begin an outer transaction
    - Bind a Session to that connection
    - Start a nested transaction (SAVEPOINT) on the Session
    - Listen for `after_transaction_end` to restart the nested transaction when it ends
    - On teardown: close session, rollback outer transaction, and close connection

    This pattern is resilient and avoids SAWarning about deassociated transactions.
    """
    from sqlalchemy import event

    connection = test_engine.connect()
    outer_transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False, expire_on_commit=False)
    session = SessionLocal()

    # Start a SAVEPOINT / nested transaction
    session.begin_nested()

    # When the nested transaction ends, open a new nested transaction so the session
    # stays usable for subsequent operations within the same outer transaction.
    def _restart_savepoint(sess, trans):
        # Only restart for nested transactions that were closed (not the outer one)
        if trans.nested and not trans._parent:
            try:
                sess.begin_nested()
            except Exception:
                # ignore; test teardown will handle cleanup
                pass

    event.listen(session, "after_transaction_end", _restart_savepoint)

    try:
        yield session
    finally:
        # Remove listener to avoid leaking state across tests
        try:
            event.remove(session, "after_transaction_end", _restart_savepoint)
        except Exception:
            pass

        # Roll back any transactional state in the session and close it
        with contextlib.suppress(Exception):
            session.rollback()
        with contextlib.suppress(Exception):
            session.close()

        # Rollback the outer connection-level transaction and close connection
        try:
            if getattr(outer_transaction, "is_active", False):
                outer_transaction.rollback()
        except Exception:
            pass
        with contextlib.suppress(Exception):
            connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient using the per-test db_session via dependency override."""
    from fastapi.testclient import TestClient

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def client_no_db():
    """FastAPI TestClient without DB dependency override, for routes not touching DB."""
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
