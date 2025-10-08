import pytest


@pytest.fixture
def sample_transaction_create_data():
    """Sample data for creating a transaction.

    Returns:
        dict: Valid transaction creation data.
    """
    return {
        "amount": 25.50,
        "currency": "EUR",
        "description": "Groceries at Albert Heijn",
        "transaction_type": "DEBIT_CARD",
        "counterparty_name": "Albert Heijn",
        "counterparty_iban": "NL91ABNA0417164300",
        "external_source": "bunq",
        "external_id": "bunq_12345",
        "category": "groceries",
    }


@pytest.fixture
def sample_transaction_create_invalid_data():
    """Sample data for creating an Invalid transaction.

    Returns:
        dict: Invalid transaction creation data.
    """
    return {
        "amount": "25.50",
        "currency": "EUR",
        "description": "Groceries at Albert Heijn",
        "transaction_type": "DEBIT_CARD",
        "counterparty_name": "Albert Heijn",
        "counterparty_iban": "NL91ABNA0417164300",
        "external_source": "bunq",
        "external_id": "bunq_12345",
        "category": "groceries",
    }


@pytest.fixture
def sample_transaction_create_minimal():
    """Minimal sample data for creating a transaction.

    Returns:
        dict: Minimal valid transaction creation data.
    """
    return {
        "amount": 10.00,
        "currency": "USD",
        "description": "Test transaction",
    }
