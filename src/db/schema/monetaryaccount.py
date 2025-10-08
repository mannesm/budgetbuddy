from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.schema.base import ModelBase


class MonetaryAccount(ModelBase):
    """MonetaryAccount model representing financial accounts.

    Stores information about user accounts from external
    sources like Bunq.
    """

    __tablename__ = "monetary_accounts"

    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str | None] = mapped_column(String(50))  # e.g., 'savings', 'checking'

    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    iban: Mapped[str | None] = mapped_column(String(34), unique=True, index=True)
    bic: Mapped[str | None] = mapped_column(String(11))
    account_status: Mapped[str | None] = mapped_column(String(50))  # e.g., 'ACTIVE', 'CLOSED'

    external_source: Mapped[str | None] = mapped_column(String(50))  # 'bunq', etc.
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)

    external_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    notes: Mapped[str | None] = mapped_column(String)
