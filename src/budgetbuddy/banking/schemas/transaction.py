"""Transaction schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    amount: float | None = Field(None, description="Transaction amount")
    currency: str | None = Field(None, min_length=3, max_length=3, description="Currency code (ISO 4217)")
    description: str | None = Field(None, description="Transaction description")
    transaction_type: str | None = Field(None, description="Type of transaction")
    counterparty_name: str | None = Field(None, description="Name of counterparty")
    counterparty_iban: str | None = Field(None, description="IBAN of counterparty")
    category: str | None = Field(None, description="Transaction category")
    tags: str | None = Field(None, description="Comma-separated tags")
    notes: str | None = Field(None, description="Additional notes")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""

    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (ISO 4217)")
    external_source: str | None = Field(None, description="External source system")
    external_id: str | None = Field(None, description="External system ID for idempotency")
    external_created_at: datetime | None = Field(None, description="Creation time in external system")
    external_updated_at: datetime | None = Field(None, description="Update time in external system")


class TransactionUpdate(TransactionBase):
    """Schema for updating a transaction (all fields optional)."""

    pass


class TransactionRead(TransactionBase):
    """Schema for reading a transaction from the API."""

    itemid: UUID
    createdtimestamp: datetime
    updatedtimestamp: datetime
    external_source: str | None = None
    external_id: str | None = None
    external_created_at: datetime | None = None
    external_updated_at: datetime | None = None

    class Config:
        from_attributes = True
