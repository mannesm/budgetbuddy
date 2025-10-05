from sqlalchemy import text

from src.budgetbuddy.db.base import DEFAULT_SCHEMA, Base

# Import models to ensure they are registered with the Base metadata
from src.budgetbuddy.db.models.transactions import Transaction  # noqa: F401
from src.budgetbuddy.db.session import engine


def create_schema_and_tables() -> None:
    # Ensure the schema exists (PostgreSQL)
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DEFAULT_SCHEMA}"))
    # Create all tables
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_schema_and_tables()
