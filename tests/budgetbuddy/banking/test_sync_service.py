"""Tests for BunqSyncService."""

from unittest.mock import Mock, patch

import pytest
from src.budgetbuddy.banking.bunq.sync_service import BunqSyncService
from src.budgetbuddy.schemas.transaction import TransactionCreate


@pytest.mark.integration
class TestBunqSyncService:
    """Integration tests for BunqSyncService."""

    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqClient")
    def test_sync_service_initialization(self, mock_client_cls):
        """Test sync service initializes with config path."""
        config_path = "/path/to/config.conf"

        service = BunqSyncService(config_path)

        mock_client_cls.assert_called_once_with(config_path)
        assert service.client is not None

    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqClient")
    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqPaymentAdapter")
    @patch("src.budgetbuddy.banking.bunq.sync_service.create_transactions_bulk")
    def test_sync_all_payments_success(self, mock_bulk_create, mock_adapter, mock_client_cls, db_session):
        """Test successful sync of all payments."""
        # Setup mocks
        mock_payment1 = Mock()
        mock_payment2 = Mock()
        mock_payments = [mock_payment1, mock_payment2]

        mock_client = Mock()
        mock_client.fetch_all_payments.return_value = mock_payments
        mock_client_cls.return_value = mock_client

        transaction1 = TransactionCreate(
            amount=10.0, currency="EUR", description="Payment 1", external_source="bunq", external_id="bunq_1"
        )
        transaction2 = TransactionCreate(
            amount=20.0, currency="EUR", description="Payment 2", external_source="bunq", external_id="bunq_2"
        )
        mock_adapter.to_transaction_creates.return_value = [transaction1, transaction2]

        mock_bulk_create.return_value = (2, 0)  # 2 inserted, 0 skipped

        # Execute
        service = BunqSyncService("/path/to/config.conf")
        stats = service.sync_all_payments(db_session)

        # Verify
        assert stats["fetched"] == 2
        assert stats["inserted"] == 2
        assert stats["skipped"] == 0

        mock_client.fetch_all_payments.assert_called_once_with(ma_status_filter="ACTIVE")
        mock_adapter.to_transaction_creates.assert_called_once_with(mock_payments)
        mock_bulk_create.assert_called_once()

    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqClient")
    def test_sync_all_payments_no_payments(self, mock_client_cls, db_session):
        """Test sync when no payments are fetched."""
        mock_client = Mock()
        mock_client.fetch_all_payments.return_value = []
        mock_client_cls.return_value = mock_client

        service = BunqSyncService("/path/to/config.conf")
        stats = service.sync_all_payments(db_session)

        assert stats["fetched"] == 0
        assert stats["inserted"] == 0
        assert stats["skipped"] == 0

    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqClient")
    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqPaymentAdapter")
    @patch("src.budgetbuddy.banking.bunq.sync_service.create_transactions_bulk")
    def test_sync_with_duplicates(self, mock_bulk_create, mock_adapter, mock_client_cls, db_session):
        """Test sync handles duplicates correctly."""
        # Setup
        mock_payment = Mock()
        mock_client = Mock()
        mock_client.fetch_all_payments.return_value = [mock_payment]
        mock_client_cls.return_value = mock_client

        transaction = TransactionCreate(
            amount=10.0, currency="EUR", description="Payment", external_source="bunq", external_id="bunq_duplicate"
        )
        mock_adapter.to_transaction_creates.return_value = [transaction]

        # Simulate 0 inserted (duplicate), 1 skipped
        mock_bulk_create.return_value = (0, 1)

        # Execute
        service = BunqSyncService("/path/to/config.conf")
        stats = service.sync_all_payments(db_session)

        # Verify
        assert stats["fetched"] == 1
        assert stats["inserted"] == 0
        assert stats["skipped"] == 1

    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqClient")
    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqPaymentAdapter")
    @patch("src.budgetbuddy.banking.bunq.sync_service.create_transactions_bulk")
    def test_sync_custom_account_filter(self, mock_bulk_create, mock_adapter, mock_client_cls, db_session):
        """Test sync respects custom account status filter."""
        mock_client = Mock()
        mock_client.fetch_all_payments.return_value = []
        mock_client_cls.return_value = mock_client

        service = BunqSyncService("/path/to/config.conf")
        service.sync_all_payments(db_session, account_status_filter="ALL")

        mock_client.fetch_all_payments.assert_called_once_with(ma_status_filter="ALL")


@pytest.mark.integration
class TestBunqSyncServiceEndToEnd:
    """End-to-end integration test with real database."""

    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqClient")
    def test_full_sync_pipeline(self, mock_client_cls, db_session, mock_bunq_payments):
        """Test complete sync pipeline with database."""
        from src.db.schema.transaction import Transaction

        # Setup mock client
        mock_client = Mock()
        mock_client.fetch_all_payments.return_value = mock_bunq_payments
        mock_client_cls.return_value = mock_client

        # Execute sync
        service = BunqSyncService("/path/to/config.conf")
        stats = service.sync_all_payments(db_session)

        # Verify stats
        assert stats["fetched"] == 2
        assert stats["inserted"] == 2
        assert stats["skipped"] == 0

        # Verify database
        transactions = db_session.query(Transaction).filter(Transaction.external_source == "bunq").all()

        assert len(transactions) == 2
        assert any(tx.external_id == "bunq_12345" for tx in transactions)
        assert any(tx.external_id == "bunq_67890" for tx in transactions)

    @patch("src.budgetbuddy.banking.bunq.sync_service.BunqClient")
    def test_idempotency_double_sync(self, mock_client_cls, db_session, mock_bunq_payments):
        """Test running sync twice doesn't create duplicates."""
        from src.db.schema.transaction import Transaction

        mock_client = Mock()
        mock_client.fetch_all_payments.return_value = mock_bunq_payments
        mock_client_cls.return_value = mock_client

        service = BunqSyncService("/path/to/config.conf")

        # First sync
        stats1 = service.sync_all_payments(db_session)
        assert stats1["inserted"] == 2

        # Second sync (same data)
        stats2 = service.sync_all_payments(db_session)
        assert stats2["inserted"] == 0
        assert stats2["skipped"] == 2

        # Verify only 2 transactions exist
        transactions = db_session.query(Transaction).filter(Transaction.external_source == "bunq").all()
        assert len(transactions) == 2
