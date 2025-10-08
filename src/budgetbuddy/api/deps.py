from collections.abc import Iterator

from sqlalchemy.orm import Session
from src.db.session import SessionLocal


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
