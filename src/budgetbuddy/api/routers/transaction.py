from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.budgetbuddy.api.deps import get_db
from src.budgetbuddy.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from src.db import Transaction
from src.db.repository.base import CRUDRepository

router = APIRouter(prefix="/transactions", tags=["transactions"])
repo = CRUDRepository[Transaction](Transaction)


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)) -> Transaction:
    return repo.create(db, payload.model_dump())


@router.get("/", response_model=list[TransactionRead])
def list_transactions(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Sequence[Transaction]:
    return repo.list(db, offset=offset, limit=limit)


@router.get("/{itemid}", response_model=TransactionRead)
def get_transaction(itemid: UUID, db: Session = Depends(get_db)) -> Transaction:
    tx = repo.get(db, itemid)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.patch("/{itemid}", response_model=TransactionRead)
def update_transaction(itemid: UUID, payload: TransactionUpdate, db: Session = Depends(get_db)) -> Transaction:
    tx = repo.get(db, itemid)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return repo.update(db, tx, data)


@router.delete("/{itemid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(itemid: UUID, db: Session = Depends(get_db)) -> None:
    tx = repo.get(db, itemid)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    repo.delete(db, tx)
    return None
