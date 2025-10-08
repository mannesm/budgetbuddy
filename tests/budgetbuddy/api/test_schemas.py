"""Tests for transaction API schemas."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.budgetbuddy.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)


@pytest.mark.unit
class TestTransactionCreate:
    """Tests for TransactionCreate schema."""

    def test_create_with_required_fields_only(self):
        """Test creating transaction with only required fields."""
        data = {
            "amount": 10.50,
            "currency": "EUR",
        }

        tx = TransactionCreate(**data)

        assert tx.amount == 10.50
        assert tx.currency == "EUR"
        assert tx.description is None
        assert tx.external_source is None

    def test_create_with_all_fields(self, sample_transaction_create_data):
        """Test creating transaction with all fields."""
        tx = TransactionCreate(**sample_transaction_create_data)

        assert tx.amount == 25.50
        assert tx.currency == "EUR"
        assert tx.description == "Groceries at Albert Heijn"
        assert tx.transaction_type == "DEBIT_CARD"
        assert tx.counterparty_name == "Albert Heijn"
        assert tx.counterparty_iban == "NL91ABNA0417164300"
        assert tx.external_source == "bunq"
        assert tx.external_id == "bunq_12345"
        assert tx.category == "groceries"

    def test_create_validates_currency_length(self):
        """Test currency must be 3 characters."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(amount=10.0, currency="EURO", description=None)

        assert "currency" in str(exc_info.value)

    def test_create_accepts_short_currency(self):
        """Test currency validation accepts 3-char codes."""
        tx = TransactionCreate(amount=10.0, currency="USD")
        assert tx.currency == "USD"

    def test_model_dump_excludes_none(self):
        """Test model_dump with exclude_none for cleaner data."""
        tx = TransactionCreate(amount=10.0, currency="EUR", description="Test")

        dumped = tx.model_dump(exclude_none=True)

        assert "amount" in dumped
        assert "currency" in dumped
        assert "description" in dumped
        # Optional fields not set should be excluded
        assert "category" not in dumped or dumped["category"] is None


@pytest.mark.unit
class TestTransactionUpdate:
    """Tests for TransactionUpdate schema."""

    def test_update_all_fields_optional(self):
        """Test all fields are optional in update schema."""
        tx = TransactionUpdate()

        assert tx.amount is None
        assert tx.currency is None
        assert tx.description is None

    def test_update_partial_fields(self):
        """Test updating only some fields."""
        tx = TransactionUpdate(description="Updated description", category="updated_category")

        assert tx.description == "Updated description"
        assert tx.category == "updated_category"
        assert tx.amount is None

    def test_update_validates_currency_length(self):
        """Test currency validation on update."""
        with pytest.raises(ValidationError):
            TransactionUpdate(currency="TOOLONG")

    def test_update_model_dump_exclude_none(self):
        """Test model_dump excludes unset fields."""
        tx = TransactionUpdate(description="New desc")

        dumped = tx.model_dump(exclude_none=True)

        assert "description" in dumped
        assert "amount" not in dumped
        assert "currency" not in dumped


@pytest.mark.unit
class TestTransactionRead:
    """Tests for TransactionRead schema."""

    def test_read_from_orm(self, db_session):
        """Test TransactionRead can be created from ORM model."""
        from src.db.schema.transaction import Transaction

        tx = Transaction(
            amount=15.00, currency="EUR", description="Test", external_source="bunq", external_id="bunq_123"
        )
        db_session.add(tx)
        db_session.commit()
        db_session.refresh(tx)

        read = TransactionRead.model_validate(tx)

        assert read.itemid == tx.itemid
        assert read.amount == 15.00
        assert read.currency == "EUR"
        assert read.description == "Test"
        assert read.external_source == "bunq"
        assert read.external_id == "bunq_123"
        assert isinstance(read.createdtimestamp, datetime)
        assert isinstance(read.updatedtimestamp, datetime)

    def test_read_includes_all_fields(self):
        """Test TransactionRead schema includes all expected fields."""
        data = {
            "itemid": uuid4(),
            "createdtimestamp": datetime.now(),
            "updatedtimestamp": datetime.now(),
            "amount": 25.50,
            "currency": "EUR",
            "description": "Test",
            "transaction_type": "IDEAL",
            "counterparty_name": "Store",
            "counterparty_iban": "NL00TEST",
            "external_source": "bunq",
            "external_id": "bunq_123",
            "external_created_at": datetime.now(),
            "external_updated_at": datetime.now(),
            "category": "groceries",
            "tags": "food,shopping",
            "notes": "Test notes",
        }

        read = TransactionRead(**data)

        assert read.amount == 25.50
        assert read.category == "groceries"
        assert read.tags == "food,shopping"
