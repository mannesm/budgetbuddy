"""Tests for BunqClient."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.budgetbuddy.banking.bunq.fetch import BunqClient


@pytest.mark.unit
class TestBunqClientInitialization:
    """Tests for BunqClient initialization."""

    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    def test_client_initialization_with_string_path(self, mock_bunq_ctx, mock_api_ctx):
        """Test client initializes with string path."""
        config_path = "/path/to/config.conf"

        client = BunqClient(config_path)

        assert client.config_path == Path(config_path)
        mock_api_ctx.restore.assert_called_once_with(config_path)
        mock_bunq_ctx.load_api_context.assert_called_once()

    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    def test_client_initialization_with_path_object(self, mock_bunq_ctx, mock_api_ctx):
        """Test client initializes with Path object."""
        config_path = Path("/path/to/config.conf")

        client = BunqClient(config_path)

        assert client.config_path == config_path
        mock_api_ctx.restore.assert_called_once()


@pytest.mark.unit
class TestBunqClientListAccounts:
    """Tests for listing monetary accounts."""

    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.MonetaryAccountBankApiObject")
    @patch("src.budgetbuddy.banking.bunq.fetch.MonetaryAccountSavingsApiObject")
    def test_list_all_monetary_accounts(self, mock_savings, mock_bank, mock_api_ctx, mock_bunq_ctx):
        """Test listing all monetary accounts."""
        # Setup mocks
        bank_account = Mock()
        bank_account.status = "ACTIVE"
        bank_response = Mock()
        bank_response.value = [bank_account]
        mock_bank.list.return_value = bank_response

        savings_account = Mock()
        savings_account.status = "ACTIVE"
        savings_response = Mock()
        savings_response.value = [savings_account]
        mock_savings.list.return_value = savings_response

        client = BunqClient("/path/to/config.conf")
        accounts = client.list_all_monetary_accounts()

        assert len(accounts) == 2
        assert bank_account in accounts
        assert savings_account in accounts

    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.MonetaryAccountBankApiObject")
    @patch("src.budgetbuddy.banking.bunq.fetch.MonetaryAccountSavingsApiObject")
    def test_list_accounts_with_status_filter(self, mock_savings, mock_bank, mock_api_ctx, mock_bunq_ctx):
        """Test listing accounts filters by status."""
        # Setup mocks
        active_account = Mock()
        active_account.status = "ACTIVE"

        closed_account = Mock()
        closed_account.status = "CLOSED"

        bank_response = Mock()
        bank_response.value = [active_account, closed_account]
        mock_bank.list.return_value = bank_response
        mock_savings.list.return_value = Mock(value=[])

        client = BunqClient("/path/to/config.conf")
        accounts = client.list_all_monetary_accounts(status="ACTIVE")

        assert len(accounts) == 1
        assert active_account in accounts
        assert closed_account not in accounts


@pytest.mark.unit
class TestBunqClientFetchPayments:
    """Tests for fetching payments."""

    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.PaymentApiObject")
    @patch("src.budgetbuddy.banking.bunq.fetch.Pagination")
    def test_fetch_payments_for_account_single_page(
        self, mock_pagination_cls, mock_payment, mock_api_ctx, mock_bunq_ctx
    ):
        """Test fetching payments when all fit in one page."""
        # Setup mocks
        payment1 = Mock()
        payment2 = Mock()

        response = Mock()
        response.value = [payment1, payment2]
        response.pagination = Mock()
        response.pagination.has_previous_page.return_value = False

        mock_payment.list.return_value = response
        mock_pagination_cls.return_value = Mock(count=50, url_params_count_only={})

        client = BunqClient("/path/to/config.conf")
        payments = client.fetch_payments_for_account(123)

        assert len(payments) == 2
        assert payment1 in payments
        assert payment2 in payments

    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.PaymentApiObject")
    @patch("src.budgetbuddy.banking.bunq.fetch.Pagination")
    def test_fetch_payments_multiple_pages(self, mock_pagination_cls, mock_payment, mock_api_ctx, mock_bunq_ctx):
        """Test fetching payments across multiple pages."""
        # First page
        payment1 = Mock()
        response1 = Mock()
        response1.value = [payment1]
        pagination1 = Mock()
        pagination1.has_previous_page.return_value = True
        pagination1.url_params_previous_page = {"page": 2}
        response1.pagination = pagination1

        # Second page (last)
        payment2 = Mock()
        response2 = Mock()
        response2.value = [payment2]
        pagination2 = Mock()
        pagination2.has_previous_page.return_value = False
        response2.pagination = pagination2

        mock_payment.list.side_effect = [response1, response2]
        mock_pagination_cls.return_value = Mock(count=1, url_params_count_only={})

        client = BunqClient("/path/to/config.conf")
        payments = client.fetch_payments_for_account(123, page_size=1)

        assert len(payments) == 2
        assert payment1 in payments
        assert payment2 in payments

    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.PaymentApiObject")
    def test_fetch_payments_api_failure(self, mock_payment, mock_api_ctx, mock_bunq_ctx):
        """Test handling of API failure when fetching payments."""
        mock_payment.list.return_value = None

        client = BunqClient("/path/to/config.conf")
        payments = client.fetch_payments_for_account(123)

        assert payments == []


@pytest.mark.unit
class TestBunqClientFetchAllPayments:
    """Tests for fetch_all_payments method."""

    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    def test_fetch_all_payments_from_multiple_accounts(self, mock_api_ctx, mock_bunq_ctx):
        """Test fetching payments from all accounts."""
        client = BunqClient("/path/to/config.conf")

        # Mock accounts
        account1 = Mock()
        account1.id_ = 1
        account2 = Mock()
        account2.id_ = 2

        # Mock methods
        client.list_all_monetary_accounts = Mock(return_value=[account1, account2])

        payment1 = Mock()
        payment2 = Mock()
        payment3 = Mock()
        client.fetch_payments_for_account = Mock(side_effect=[[payment1, payment2], [payment3]])

        all_payments = client.fetch_all_payments()

        assert len(all_payments) == 3
        assert all([p in all_payments for p in [payment1, payment2, payment3]])
        assert client.fetch_payments_for_account.call_count == 2

    @patch("src.budgetbuddy.banking.bunq.fetch.BunqContext")
    @patch("src.budgetbuddy.banking.bunq.fetch.ApiContext")
    def test_fetch_all_payments_skips_account_without_id(self, mock_api_ctx, mock_bunq_ctx):
        """Test that accounts without IDs are skipped."""
        client = BunqClient("/path/to/config.conf")

        # Mock accounts - one without ID
        account_with_id = Mock()
        account_with_id.id_ = 1
        account_without_id = Mock(spec=[])  # No id_ attribute

        client.list_all_monetary_accounts = Mock(return_value=[account_with_id, account_without_id])
        client.fetch_payments_for_account = Mock(return_value=[Mock()])

        all_payments = client.fetch_all_payments()

        assert len(all_payments) == 1
        assert client.fetch_payments_for_account.call_count == 1
