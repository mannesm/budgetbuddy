# python
from sqlalchemy.orm import Session
from src.budgetbuddy.db.repository.base import CRUDRepository
from src.budgetbuddy.db.schema.transaction import Transaction

repo = CRUDRepository[Transaction](Transaction)


def _validate_create_payload(data: dict) -> None:
    currency = data.get("currency")
    if not isinstance(currency, str) or not currency.strip():
        raise ValueError("currency is required and must be a non-empty string")

    amount = data.get("amount")
    if not isinstance(amount, (int | float)):
        raise ValueError("amount is required and must be a number")

    if amount <= 0:
        raise ValueError("amount must be greater than 0")


def create_transaction(db: Session, data: dict) -> Transaction:
    _validate_create_payload(data)
    return repo.create(db, data)


def update_transaction(db: Session, itemid, data: dict) -> Transaction | None:
    tx = repo.get(db, itemid)
    if not tx:
        return None
    return repo.update(db, tx, data)
