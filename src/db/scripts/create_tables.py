from sqlalchemy import text
from src.db.schema.base import DEFAULT_SCHEMA, Base
from src.db.schema.transaction import Transaction  # noqa: F401
from src.db.session import engine


def create_schema_and_tables() -> None:
    # Ensure the schema exists (PostgreSQL)
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DEFAULT_SCHEMA}"))
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_schema_and_tables()
