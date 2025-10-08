from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.schema.base import ModelBase


class Transaction(ModelBase):
    """Transaction model representing financial transactions.

    Stores both manual transactions and those imported from external
    sources like Bunq.
    """

    __tablename__ = "transactions"

    # Core financial fields
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    description: Mapped[str | None] = mapped_column(String)

    # Transaction metadata
    transaction_type: Mapped[str | None] = mapped_column(String(50))
    counterparty_name: Mapped[str | None] = mapped_column(String(255))
    counterparty_iban: Mapped[str | None] = mapped_column(String(34))

    # External system tracking (for idempotency)
    external_source: Mapped[str | None] = mapped_column(String(50))  # 'bunq', 'manual', etc.
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)

    # Original transaction timestamps from external system
    external_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Additional metadata
    category: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[str | None] = mapped_column(String)  # JSON or comma-separated
    notes: Mapped[str | None] = mapped_column(String)
