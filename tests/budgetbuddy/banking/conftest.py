"""Fixtures and utilities for banking tests."""

from datetime import datetime
from unittest.mock import Mock

import pytest
from bunq.sdk.model.generated.endpoint import PaymentApiObject
from bunq.sdk.model.generated.object_ import (
    AmountObject as Amount,
)
from bunq.sdk.model.generated.object_ import (
    LabelMonetaryAccountObject as LabelMonetaryAccount,
)
from bunq.sdk.model.generated.object_ import (
    PointerObject as Pointer,
)


@pytest.fixture
def mock_bunq_payment():
    """Create a mock Bunq PaymentApiObject for testing.

    Returns:
        Mock: A mock payment object with typical Bunq structure.
    """
    payment = Mock(spec=PaymentApiObject)
    payment.id_ = 12345
    payment.created = datetime(2025, 10, 1, 12, 0, 0)
    payment.updated = datetime(2025, 10, 2, 14, 30, 0)
    payment.description = "Coffee at Starbucks"
    payment.type_ = "IDEAL"

    # Mock amount
    payment.amount = Mock(spec=Amount)
    payment.amount.value = "15.50"
    payment.amount.currency = "EUR"

    # Mock counterparty
    payment.counterparty_alias = Mock(spec=Pointer)
    payment.counterparty_alias.label_monetary_account = Mock(spec=LabelMonetaryAccount)
    payment.counterparty_alias.label_monetary_account.display_name = "Starbucks Amsterdam"
    payment.counterparty_alias.label_monetary_account.iban = "NL21INGB0001234567"

    return payment


@pytest.fixture
def mock_bunq_payment_minimal():
    """Create a minimal mock Bunq payment with only required fields.

    Returns:
        Mock: A minimal mock payment object.
    """
    payment = Mock(spec=PaymentApiObject)
    payment.id_ = 67890
    payment.created = None
    payment.updated = None
    payment.description = None
    payment.type_ = None

    payment.amount = Mock(spec=Amount)
    payment.amount.value = "5.00"
    payment.amount.currency = "USD"

    payment.counterparty_alias = None

    return payment


@pytest.fixture
def mock_bunq_payments(mock_bunq_payment, mock_bunq_payment_minimal):
    """Create a list of mock Bunq payments.

    Returns:
        list: List of mock payment objects.
    """
    return [mock_bunq_payment, mock_bunq_payment_minimal]
