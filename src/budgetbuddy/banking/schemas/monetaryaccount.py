"""Monetaryaccount schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MonetaryAccountBase(BaseModel):
    account_name: str | None = None
    account_type: str | None = None
    currency: str | None = None
    balance: float | None = None
    iban: str | None = None
    bic: str | None = None
    account_status: str | None = None
    notes: str | None = None
    description: str | None = None
    external_source: str | None = None
    external_id: str | None = None
    external_created_at: datetime | None = None
    external_updated_at: datetime | None = None


class MonetaryAccountCreate(MonetaryAccountBase):
    """Schema for creating a new MonetaryAccount."""

    pass


class MonetaryAccountUpdate(MonetaryAccountBase):
    """Schema for updating a MonetaryAccount (all fields optional)."""

    pass


class MonetaryAccountRead(MonetaryAccountBase):
    """Schema for reading a MonetaryAccount from the API."""

    class Config:
        from_attributes = True
