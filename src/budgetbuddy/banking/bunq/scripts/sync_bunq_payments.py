"""Script to sync Bunq payments to database.

Usage:
    python -m src.budgetbuddy.banking.bunq.scripts.sync_bunq_payments
"""

import os
from pathlib import Path

from src.budgetbuddy.banking.bunq.sync_service import BunqSyncService
from src.common.log.logger import get_logger
from src.db.session import SessionLocal

logger = get_logger(__name__)


def main():
    """Sync all Bunq payments to the database."""
    # Get config path from environment or use default
    config_path = os.getenv("BUNQ_CONFIG_PATH", Path.home() / ".bunq" / "bunq_api_context.conf")

    logger.info("Starting Bunq payment sync with config: %s", config_path)

    sync_service = BunqSyncService(config_path)

    with SessionLocal() as session:
        stats = sync_service.sync_all_payments(db=session, account_status_filter="ACTIVE")

    # Report results
    logger.info("=" * 50)
    logger.info("SYNC SUMMARY")
    logger.info("=" * 50)
    logger.info("Payments fetched from Bunq: %d", stats["fetched"])
    logger.info("New transactions inserted:  %d", stats["inserted"])
    logger.info("Duplicates skipped:         %d", stats["skipped"])
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
