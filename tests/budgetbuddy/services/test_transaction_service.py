"""Enhanced tests for transaction service with new functionality."""

from datetime import UTC, datetime

import pytest
from src.budgetbuddy.schemas.transaction import TransactionCreate, TransactionUpdate
from src.budgetbuddy.services.transaction_service import (
    create_transaction,
    create_transactions_bulk,
    get_transaction_by_external_id,
    list_transactions,
    repo,
    update_transaction,
)
from src.db.schema.transaction import Transaction


@pytest.mark.integration
class TestCreateTransaction:
    """Tests for create_transaction function."""

    def test_create_transaction_with_pydantic_model(self, db_session):
        """Test creating transaction with Pydantic model."""
        data = TransactionCreate(amount=3.5, currency="EUR", description="water")

        tx = create_transaction(db_session, data)

        assert isinstance(tx, Transaction)
        assert tx.amount == 3.5
        assert tx.currency == "EUR"
        assert tx.description == "water"

    def test_create_transaction_with_external_fields(self, db_session):
        """Test creating transaction with external source tracking."""
        data = TransactionCreate(
            amount=15.50,
            currency="EUR",
            description="Coffee",
            external_source="bunq",
            external_id="bunq_12345",
            counterparty_name="Starbucks",
        )

        tx = create_transaction(db_session, data)

        assert tx.external_source == "bunq"
        assert tx.external_id == "bunq_12345"
        assert tx.counterparty_name == "Starbucks"

    def test_create_transaction_amount_validation(self, db_session):
        """Test amount must be greater than 0."""
        data = TransactionCreate(amount=0, currency="EUR", description="Invalid")

        with pytest.raises(ValueError, match="amount must be greater than 0"):
            create_transaction(db_session, data)

    def test_create_transaction_negative_amount(self, db_session):
        """Test negative amounts are rejected."""
        data = TransactionCreate(amount=-10.0, currency="EUR", description="Invalid")

        with pytest.raises(ValueError):
            create_transaction(db_session, data)


@pytest.mark.integration
class TestBulkCreateTransactions:
    """Tests for create_transactions_bulk function."""

    def test_bulk_create_multiple_transactions(self, db_session):
        """Test bulk inserting multiple transactions."""
        transactions = [
            TransactionCreate(
                amount=10.0,
                currency="EUR",
                description=f"Transaction {i}",
                external_source="bunq",
                external_id=f"bunq_{i}",
            )
            for i in range(5)
        ]

        inserted, skipped = create_transactions_bulk(db_session, transactions)

        assert inserted == 5
        assert skipped == 0

    def test_bulk_create_with_duplicates(self, db_session):
        """Test bulk insert skips duplicates based on external_id."""
        transactions = [
            TransactionCreate(
                amount=10.0, currency="EUR", description="First", external_source="bunq", external_id="bunq_duplicate"
            )
        ]

        # First insert
        inserted1, skipped1 = create_transactions_bulk(db_session, transactions)
        assert inserted1 == 1
        assert skipped1 == 0

        # Second insert (same external_id)
        inserted2, skipped2 = create_transactions_bulk(db_session, transactions)
        assert inserted2 == 0
        assert skipped2 == 1

    def test_bulk_create_empty_list(self, db_session):
        """Test bulk insert with empty list returns zero counts."""
        inserted, skipped = create_transactions_bulk(db_session, [])

        assert inserted == 0
        assert skipped == 0

    def test_bulk_create_mixed_duplicates(self, db_session):
        """Test bulk insert with mix of new and duplicate transactions."""
        # Insert initial transactions
        initial = [
            TransactionCreate(
                amount=10.0,
                currency="EUR",
                description=f"Initial {i}",
                external_source="bunq",
                external_id=f"bunq_initial_{i}",
            )
            for i in range(3)
        ]
        create_transactions_bulk(db_session, initial)

        # Try to insert mix of duplicates and new
        mixed = [
            TransactionCreate(
                amount=10.0,
                currency="EUR",
                description="Initial 1",  # Duplicate
                external_source="bunq",
                external_id="bunq_initial_1",
            ),
            TransactionCreate(
                amount=20.0,
                currency="EUR",
                description="New transaction",  # New
                external_source="bunq",
                external_id="bunq_new_1",
            ),
            TransactionCreate(
                amount=10.0,
                currency="EUR",
                description="Initial 2",  # Duplicate
                external_source="bunq",
                external_id="bunq_initial_2",
            ),
        ]

        inserted, skipped = create_transactions_bulk(db_session, mixed)

        assert inserted == 1  # Only the new one
        assert skipped == 2  # Two duplicates

    def test_bulk_create_performance(self, db_session):
        """Test bulk insert is efficient with many transactions."""
        import time

        # Create 100 transactions
        transactions = [
            TransactionCreate(
                amount=float(i),
                currency="EUR",
                description=f"Perf test {i}",
                external_source="bunq",
                external_id=f"bunq_perf_{i}",
            )
            for i in range(100)
        ]

        start = time.time()
        inserted, skipped = create_transactions_bulk(db_session, transactions)
        elapsed = time.time() - start

        assert inserted == 100
        assert skipped == 0
        assert elapsed < 1.0  # Should complete in under 1 second


@pytest.mark.integration
class TestUpdateTransaction:
    """Tests for update_transaction function."""

    def test_update_with_pydantic_model(self, db_session):
        """Test updating transaction with Pydantic model."""
        # Create
        data = TransactionCreate(amount=10.0, currency="EUR", description="Original")
        tx = create_transaction(db_session, data)

        # Update
        update_data = TransactionUpdate(description="Updated description", category="groceries")
        updated = update_transaction(db_session, tx.itemid, update_data)

        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.category == "groceries"
        assert updated.amount == 10.0  # Unchanged

    def test_update_nonexistent_transaction(self, db_session):
        """Test updating nonexistent transaction returns None."""
        from uuid import uuid4

        update_data = TransactionUpdate(description="Won't work")
        result = update_transaction(db_session, uuid4(), update_data)

        assert result is None


@pytest.mark.integration
class TestGetTransactionByExternalId:
    """Tests for get_transaction_by_external_id function."""

    def test_get_by_external_id_found(self, db_session):
        """Test finding transaction by external source and ID."""
        data = TransactionCreate(
            amount=25.0, currency="EUR", description="Test", external_source="bunq", external_id="bunq_12345"
        )
        created = create_transaction(db_session, data)

        found = get_transaction_by_external_id(db_session, "bunq", "bunq_12345")

        assert found is not None
        assert found.itemid == created.itemid
        assert found.external_source == "bunq"
        assert found.external_id == "bunq_12345"

    def test_get_by_external_id_not_found(self, db_session):
        """Test returns None when external ID not found."""
        found = get_transaction_by_external_id(db_session, "bunq", "nonexistent_id")

        assert found is None

    def test_get_by_external_id_different_source(self, db_session):
        """Test filtering by external source works correctly."""
        data = TransactionCreate(
            amount=25.0, currency="EUR", description="Test", external_source="bunq", external_id="shared_id_123"
        )
        create_transaction(db_session, data)

        # Try to find with wrong source
        found = get_transaction_by_external_id(db_session, "revolut", "shared_id_123")

        assert found is None


# Keep existing tests for backwards compatibility
@pytest.mark.integration
def test_list_transactions_service_base(db_session):
    """Test basic transaction listing."""
    data1 = TransactionCreate(amount=3.5, currency="EUR", description="water")
    data2 = TransactionCreate(amount=7.0, currency="USD", description="snacks")

    tx1 = create_transaction(db_session, data1)
    tx2 = create_transaction(db_session, data2)

    txs = repo.list(db_session)
    assert len(txs) >= 2
    itemid_list = [tx.itemid for tx in txs]
    assert tx1.itemid in itemid_list
    assert tx2.itemid in itemid_list


@pytest.mark.integration
def test_list_transactions_service_date_range(db_session):
    """Integration test: ensure listing by start/end datetime returns the expected rows."""
    # Controlled timestamps (UTC)
    t1 = datetime(2025, 10, 1, 12, 0, tzinfo=UTC)
    t2 = datetime(2025, 10, 5, 12, 0, tzinfo=UTC)
    t3 = datetime(2025, 10, 10, 12, 0, tzinfo=UTC)

    tx1 = repo.create(
        db_session,
        {"amount": 1.0, "currency": "EUR", "description": "t1", "createdtimestamp": t1},
    )
    tx2 = repo.create(
        db_session,
        {"amount": 2.0, "currency": "EUR", "description": "t2", "createdtimestamp": t2},
    )
    tx3 = repo.create(
        db_session,
        {"amount": 3.0, "currency": "EUR", "description": "t3", "createdtimestamp": t3},
    )

    # Inclusive range that should include t1 and t2 but not t3
    start = datetime(2025, 10, 1, 0, 0, tzinfo=UTC)
    end = datetime(2025, 10, 5, 23, 59, 59, tzinfo=UTC)
    res = list_transactions(db_session, start=start, end=end)
    ids = {r.itemid for r in res}

    assert tx1.itemid in ids
    assert tx2.itemid in ids
    assert tx3.itemid not in ids

    # Single-sided start: should include tx2 and tx3 but not tx1
    res2 = list_transactions(db_session, start=datetime(2025, 10, 4, 0, 0, tzinfo=UTC))
    ids2 = {r.itemid for r in res2}
    assert tx2.itemid in ids2
    assert tx3.itemid in ids2
    assert tx1.itemid not in ids2

    # start > end should raise ValueError
    with pytest.raises(ValueError):
        list_transactions(db_session, start=t3, end=t1)
