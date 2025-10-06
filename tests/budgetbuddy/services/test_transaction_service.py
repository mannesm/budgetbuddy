import pytest
from src.budgetbuddy.db.schema.transaction import Transaction
from src.budgetbuddy.services.transaction_service import create_transaction, repo


@pytest.mark.integration
def test_create_transaction_service(db_session):
    tx = create_transaction(
        db_session,
        {"amount": 3.5, "currency": "EUR", "description": "water"},
    )
    assert isinstance(tx, Transaction)

    fetched = repo.get(db_session, tx.itemid)
    assert fetched is not None and fetched.itemid == tx.itemid


@pytest.mark.integration
@pytest.mark.parametrize("currency", [None, ""])
def test_create_transaction_service_invalid_currency(db_session, currency):
    with pytest.raises(ValueError):
        create_transaction(
            db_session,
            {"amount": 3.5, "currency": currency, "description": "water"},
        )


@pytest.mark.integration
@pytest.mark.parametrize("amount", [None, "", "abc", [], {}])
def test_create_transaction_service_invalid_amount(db_session, amount):
    with pytest.raises(ValueError):
        create_transaction(
            db_session,
            {"amount": amount, "currency": "EUR", "description": "water"},
        )
