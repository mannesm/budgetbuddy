from __future__ import annotations

from sqlalchemy.orm import Session
from src.budgetbuddy.db.schema.transaction import Transaction
from src.budgetbuddy.db.session import SessionLocal


def run_demo() -> None:
    db: Session = SessionLocal()
    try:
        # Create a transaction
        created = Transaction(description="Groceries", amount=42.50, currency="EUR")
        db.add(created)
        db.commit()
        db.refresh(created)
        print("Created:", created)

        # Read by primary key
        fetched = db.get(Transaction, created.itemid)
        print("Fetched by itemid:", fetched)

        # Update the transaction
        fetched.amount = 50.00
        db.add(fetched)
        db.commit()
        db.refresh(fetched)
        print("Updated:", fetched)

        # List all transactions
        all_tx = db.query(Transaction).all()
        print("All:")
        for t in all_tx:
            print(" -", t)
    finally:
        db.close()


if __name__ == "__main__":
    run_demo()
