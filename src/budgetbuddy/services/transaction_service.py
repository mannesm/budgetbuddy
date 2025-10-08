"""Transaction service layer with business logic."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from src.budgetbuddy.schemas.transaction import TransactionCreate, TransactionUpdate
from src.common.log.logger import get_logger
from src.db.repository.base import CRUDRepository
from src.db.schema.transaction import Transaction

logger = get_logger(__name__)
repo = CRUDRepository[Transaction](Transaction)


def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
    """Create a single transaction entry in the database.

    Args:
        db (Session): Database session.
        data (TransactionCreate): Transaction data.

    Returns:
        Transaction: Created transaction.

    Raises:
        ValueError: If validation fails.
    """
    if data.amount <= 0:
        raise ValueError("amount must be greater than 0")

    return repo.create(db, data.model_dump())


def create_transactions_bulk(
    db: Session,
    transactions: list[TransactionCreate],
    skip_duplicates: bool = True,
) -> tuple[int, int]:
    """Bulk insert transactions with optional duplicate handling.

    Args:
        db (Session): Database session.
        transactions (list[TransactionCreate]): List of transactions.
        skip_duplicates (bool): If True, skip duplicates based on
            external_id. Defaults to True.

    Returns:
        tuple[int, int]: (inserted_count, skipped_count).
    """
    if not transactions:
        return (0, 0)

    stmt = insert(Transaction).values([t.model_dump() for t in transactions])

    if skip_duplicates:
        # PostgreSQL UPSERT: skip conflicts on external_id
        stmt = stmt.on_conflict_do_nothing(index_elements=["external_id"])

    result = db.execute(stmt)
    db.commit()

    inserted = result.rowcount
    skipped = len(transactions) - inserted

    logger.info(
        "Bulk insert complete: %d inserted, %d skipped (duplicates)",
        inserted,
        skipped,
    )

    return (inserted, skipped)


def list_transactions(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    start: datetime | None = None,
    end: datetime | None = None,
) -> Sequence[Transaction]:
    """List transactions, optionally filtered by createdtimestamp.

    Args:
        db (Session): Database session.
        offset (int): Pagination offset. Defaults to 0.
        limit (int): Maximum results. Defaults to 100.
        start (datetime | None): Filter by created >= start.
        end (datetime | None): Filter by created <= end.

    Returns:
        Sequence[Transaction]: List of transactions.

    Raises:
        ValueError: If start > end.
    """
    if start is not None and end is not None and start > end:
        raise ValueError("start must be <= end")

    stmt = select(Transaction)
    if start is not None:
        stmt = stmt.where(Transaction.createdtimestamp >= start)
    if end is not None:
        stmt = stmt.where(Transaction.createdtimestamp <= end)

    stmt = stmt.offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_transaction(db: Session, itemid) -> Transaction | None:
    """Get a transaction by ID.

    Args:
        db (Session): Database session.
        itemid: Transaction UUID.

    Returns:
        Transaction | None: The transaction or None if not found.
    """
    return repo.get(db, itemid)


def update_transaction(db: Session, itemid, data: TransactionUpdate) -> Transaction | None:
    """Update a transaction.

    Args:
        db (Session): Database session.
        itemid: Transaction UUID.
        data (TransactionUpdate): Update data.

    Returns:
        Transaction | None: Updated transaction or None if not found.
    """
    tx = repo.get(db, itemid)
    if not tx:
        return None

    # Only update non-None fields
    update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
    return repo.update(db, tx, update_dict)


def delete_transaction(db: Session, itemid) -> bool:
    """Delete a transaction.

    Args:
        db (Session): Database session.
        itemid: Transaction UUID.

    Returns:
        bool: True if deleted, False if not found.
    """
    tx = repo.get(db, itemid)
    if not tx:
        return False
    repo.delete(db, tx)
    return True


def get_transaction_by_external_id(db: Session, external_source: str, external_id: str) -> Transaction | None:
    """Find a transaction by external source and ID.

    Args:
        db (Session): Database session.
        external_source (str): Source system (e.g., 'bunq').
        external_id (str): External system ID.

    Returns:
        Transaction | None: The transaction or None if not found.
    """
    stmt = select(Transaction).where(
        Transaction.external_source == external_source,
        Transaction.external_id == external_id,
    )
    return db.execute(stmt).scalar_one_or_none()
