from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

import alembic.context as alembic_context
from alembic import context as _unused_context  # noqa: F401 (kept for compatibility)
from sqlalchemy import engine_from_config, pool, text

# Add project to sys.path so imports work when running from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.budgetbuddy.db.config import settings  # noqa: E402
from src.budgetbuddy.db.schema.base import DEFAULT_SCHEMA, Base  # noqa: E402

# Import models so they are registered with Base.metadata for autogeneration
from src.budgetbuddy.db.schema.transaction import Transaction  # noqa: F401, E402

# this is the Alembic Config object, which provides access to values within the .ini file in use.
config = alembic_context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Provide the database URL dynamically
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    alembic_context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with alembic_context.begin_transaction():
        alembic_context.execute(f"CREATE SCHEMA IF NOT EXISTS {DEFAULT_SCHEMA}")
        alembic_context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        alembic_context.configure(connection=connection, target_metadata=target_metadata)

        with alembic_context.begin_transaction():
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DEFAULT_SCHEMA}"))
            alembic_context.run_migrations()


if alembic_context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
