"""Service for syncing Bunq transactions to the database."""

from pathlib import Path

from sqlalchemy.orm import Session
from src.budgetbuddy.banking.bunq.adapter import BunqPaymentAdapter
from src.budgetbuddy.banking.bunq.fetch import BunqClient
from src.budgetbuddy.services.transaction_service import create_transactions_bulk
from src.common.log.logger import get_logger

logger = get_logger(__name__)


class BunqSyncService:
    """High-level service for syncing Bunq payments to database.

    Handles the full ETL pipeline:
    - Extract: Fetch payments from Bunq API
    - Transform: Convert to domain models via adapter
    - Load: Bulk insert with duplicate handling
    """

    def __init__(self, bunq_config_path: str | Path):
        """Initialize sync service.

        Args:
            bunq_config_path (str | Path): Path to Bunq API config file.
        """
        self.client = BunqClient(bunq_config_path)

    def sync_all_payments(
        self,
        db: Session,
        account_status_filter: str = "ACTIVE",
    ) -> dict[str, int]:
        """Sync all payments from Bunq to database.

        Args:
            db (Session): Database session.
            account_status_filter (str): Filter accounts by status.
                Defaults to "ACTIVE".

        Returns:
            dict[str, int]: Statistics with keys:
                - fetched: Number of payments fetched from Bunq
                - inserted: Number of new transactions inserted
                - skipped: Number of duplicates skipped
        """
        logger.info("Starting Bunq payment sync")

        # Extract: Fetch from Bunq API
        bunq_payments = self.client.fetch_all_payments(ma_status_filter=account_status_filter)

        if not bunq_payments:
            logger.warning("No payments fetched from Bunq")
            return {"fetched": 0, "inserted": 0, "skipped": 0}

        logger.info("Fetched %d payments from Bunq", len(bunq_payments))

        transaction_creates = BunqPaymentAdapter.to_transaction_creates(bunq_payments)

        inserted, skipped = create_transactions_bulk(db, transaction_creates, skip_duplicates=True)

        stats = {
            "fetched": len(bunq_payments),
            "inserted": inserted,
            "skipped": skipped,
        }

        logger.info(
            "Sync complete: %d fetched, %d inserted, %d skipped",
            stats["fetched"],
            stats["inserted"],
            stats["skipped"],
        )

        return stats
