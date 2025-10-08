"""Tests for Bunq payment adapter."""

from datetime import datetime

import pytest
from src.budgetbuddy.banking.bunq.adapter import BunqPaymentAdapter
from src.budgetbuddy.schemas.transaction import TransactionCreate


@pytest.mark.unit
def test_bunq_adapter_converts_full_payment(mock_bunq_payment):
    """Test adapter converts a complete Bunq payment to TransactionCreate."""
    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment)

    assert isinstance(result, TransactionCreate)
    assert result.amount == 15.50
    assert result.currency == "EUR"
    assert result.description == "Coffee at Starbucks"
    assert result.transaction_type == "IDEAL"
    assert result.counterparty_name == "Starbucks Amsterdam"
    assert result.counterparty_iban == "NL21INGB0001234567"
    assert result.external_source == "bunq"
    assert result.external_id == "bunq_12345"
    assert result.external_created_at == datetime(2025, 10, 1, 12, 0, 0)
    assert result.external_updated_at == datetime(2025, 10, 2, 14, 30, 0)


@pytest.mark.unit
def test_bunq_adapter_converts_minimal_payment(mock_bunq_payment_minimal):
    """Test adapter handles payment with minimal fields."""
    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment_minimal)

    assert isinstance(result, TransactionCreate)
    assert result.amount == 5.00
    assert result.currency == "USD"
    assert result.description is None
    assert result.transaction_type is None
    assert result.counterparty_name is None
    assert result.counterparty_iban is None
    assert result.external_source == "bunq"
    assert result.external_id == "bunq_67890"
    assert result.external_created_at is None
    assert result.external_updated_at is None


@pytest.mark.unit
def test_bunq_adapter_handles_negative_amount(mock_bunq_payment):
    """Test adapter converts negative amounts to absolute values."""
    mock_bunq_payment.amount.value = "-25.00"

    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment)

    assert result.amount == 25.00  # Should be absolute value


@pytest.mark.unit
def test_bunq_adapter_converts_multiple_payments(mock_bunq_payments):
    """Test adapter can convert a list of payments."""
    results = BunqPaymentAdapter.to_transaction_creates(mock_bunq_payments)

    assert len(results) == 2
    assert all(isinstance(r, TransactionCreate) for r in results)
    assert results[0].external_id == "bunq_12345"
    assert results[1].external_id == "bunq_67890"


@pytest.mark.unit
def test_bunq_adapter_handles_missing_amount(mock_bunq_payment):
    """Test adapter handles missing amount gracefully."""
    mock_bunq_payment.amount = None

    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment)

    assert result.amount == 0.0
    assert result.currency == "EUR"  # Default currency


@pytest.mark.unit
def test_bunq_adapter_external_id_format(mock_bunq_payment):
    """Test external_id follows expected format."""
    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment)

    assert result.external_id.startswith("bunq_")
    assert result.external_id == "bunq_12345"


@pytest.mark.unit
def test_bunq_adapter_extracts_counterparty_display_name_only(mock_bunq_payment):
    """Test adapter extracts counterparty when only display_name is available."""
    # Remove label_monetary_account, add display_name directly
    mock_bunq_payment.counterparty_alias.label_monetary_account = None
    mock_bunq_payment.counterparty_alias.display_name = "Direct Display Name"

    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment)

    assert result.counterparty_name == "Direct Display Name"
    assert result.counterparty_iban is None


@pytest.mark.unit
def test_bunq_adapter_extracts_counterparty_iban_only(mock_bunq_payment):
    """Test adapter extracts counterparty when only IBAN is available."""
    mock_bunq_payment.counterparty_alias.label_monetary_account = None
    mock_bunq_payment.counterparty_alias.iban = "NL00TEST0000000000"

    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment)

    assert result.counterparty_iban == "NL00TEST0000000000"


@pytest.mark.unit
def test_bunq_adapter_handles_no_counterparty_info(mock_bunq_payment):
    """Test adapter handles missing counterparty information."""
    mock_bunq_payment.counterparty_alias = None

    result = BunqPaymentAdapter.to_transaction_create(mock_bunq_payment)

    assert result.counterparty_name is None
    assert result.counterparty_iban is None
