# Centralized SQLAlchemy engine and session factory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.budgetbuddy.db.config import DATABASE_URL

# Create the engine once and reuse it
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Session factory. expire_on_commit=False keeps attributes accessible after commit.
SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)
