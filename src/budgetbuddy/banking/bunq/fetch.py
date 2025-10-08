"""Bunq API client for fetching monetary accounts and payments."""

from pathlib import Path

from bunq import Pagination
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated.endpoint import (
    MonetaryAccountBankApiObject,
    MonetaryAccountSavingsApiObject,
    PaymentApiObject,
)
from src.common.log.logger import get_logger

logger = get_logger(__name__)


class BunqClient:
    """Client for interacting with Bunq API.

    Encapsulates API context management and provides methods for
    fetching accounts and payments.
    """

    def __init__(self, config_path: str | Path):
        """Initialize Bunq client with API context.

        Args:
            config_path (str | Path): Path to bunq_api_context.conf file.
        """
        self.config_path = Path(config_path)
        self._load_context()

    def _load_context(self) -> None:
        """Load and set the Bunq API context."""
        api_context = ApiContext.restore(str(self.config_path))
        BunqContext.load_api_context(api_context)
        logger.info("Bunq API context loaded from %s", self.config_path)

    def list_all_monetary_accounts(
        self, status: str | None = None
    ) -> list[MonetaryAccountBankApiObject | MonetaryAccountSavingsApiObject]:
        """List all monetary accounts (bank + savings).

        Args:
            status (str | None): Filter by account status (e.g., 'ACTIVE').

        Returns:
            list: List of monetary account objects.
        """
        accounts = []
        logger.info("Fetching all Monetary Accounts with status filter: %s", status)

        resp = MonetaryAccountBankApiObject.list()
        if resp is not None and getattr(resp, "value", None):
            accounts.extend(resp.value)

        resp = MonetaryAccountSavingsApiObject.list()
        if resp is not None and getattr(resp, "value", None):
            accounts.extend(resp.value)

        if status:
            accounts = [acc for acc in accounts if acc.status == status]

        logger.info("Found %d monetary accounts", len(accounts))
        return accounts

    def fetch_payments_for_account(self, monetary_account_id: int, page_size: int = 50) -> list[PaymentApiObject]:
        """Fetch all payments for a specific monetary account.

        Args:
            monetary_account_id (int): ID of the monetary account.
            page_size (int): Number of payments per page. Defaults to 50.

        Returns:
            list[PaymentApiObject]: List of payment objects.
        """
        payments = []
        logger.info("Fetching payments for account %s", monetary_account_id)

        pagination = Pagination()
        pagination.count = page_size

        response = PaymentApiObject.list(
            monetary_account_id=monetary_account_id,
            params=pagination.url_params_count_only,
        )

        if response is None:
            logger.error("Failed to fetch payments for account %s", monetary_account_id)
            return payments

        payments.extend(response.value or [])
        page_info = response.pagination

        while page_info and page_info.has_previous_page():
            response = PaymentApiObject.list(
                monetary_account_id=monetary_account_id,
                params=page_info.url_params_previous_page,
            )
            payments.extend(response.value or [])
            page_info = response.pagination

        logger.info("Found %d payments for account %s", len(payments), monetary_account_id)
        return payments

    def fetch_all_payments(self, ma_status_filter: str | None = None, page_size: int = 100) -> list[PaymentApiObject]:
        """Fetch all payments from all monetary accounts.

        Args:
            ma_status_filter (str | None): Filter accounts by status.
            page_size (int): Number of payments per page. Defaults to 100.

        Returns:
            list[PaymentApiObject]: All payments from all accounts.
        """
        all_payments = []
        accounts = self.list_all_monetary_accounts(ma_status_filter)

        for account in accounts:
            acct_id = getattr(account, "id_", None) or getattr(account, "id", None)
            if not acct_id:
                logger.warning("Account has no ID, skipping: %s", account)
                continue

            account_payments = self.fetch_payments_for_account(acct_id, page_size=page_size)
            all_payments.extend(account_payments)

        logger.info("Total payments fetched: %d", len(all_payments))
        return all_payments
