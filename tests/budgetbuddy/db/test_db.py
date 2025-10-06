"""
Test database configuration helpers.

Use the fixtures in tests/budgetbuddy/conftest.py for engine/session and FastAPI client.
This module only documents the recommended TEST_DATABASE_URL shape and schema name.
"""

import os

# Name your test database distinctly from dev/prod
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "budgetbuddy_test")
TEST_SCHEMA = os.getenv("TEST_SCHEMA", "budgetbuddy")

# Example DSN. You can override via env var TEST_DATABASE_URL.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql+psycopg2://postgres:password@localhost:5432/{TEST_DB_NAME}",
)
