"""Transaction API router."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.budgetbuddy.api.deps import get_db
from src.budgetbuddy.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from src.budgetbuddy.services import transaction_service as service
from src.db.schema.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)) -> Transaction:
    """Create a new transaction."""
    try:
        return service.create_transaction(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/", response_model=list[TransactionRead])
def list_transactions(
    offset: int = 0,
    limit: int = 100,
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
) -> Sequence[Transaction]:
    """List transactions with optional date filtering."""
    try:
        return service.list_transactions(db, offset=offset, limit=limit, start=start, end=end)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{itemid}", response_model=TransactionRead)
def get_transaction(itemid: UUID, db: Session = Depends(get_db)) -> Transaction:
    """Get a single transaction by ID."""
    tx = service.get_transaction(db, itemid)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.patch("/{itemid}", response_model=TransactionRead)
def update_transaction(itemid: UUID, payload: TransactionUpdate, db: Session = Depends(get_db)) -> Transaction:
    """Update a transaction."""
    tx = service.update_transaction(db, itemid, payload)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.delete("/{itemid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(itemid: UUID, db: Session = Depends(get_db)) -> None:
    """Delete a transaction."""
    deleted = service.delete_transaction(db, itemid)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return None
