from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str
    description: str | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: float | None = Field(None, gt=0)
    currency: str | None = None
    description: str | None = None


class TransactionRead(BaseModel):
    itemid: UUID
    createdtimestamp: datetime
    updatedtimestamp: datetime
    amount: float
    currency: str
    description: str | None = None

    class Config:
        from_attributes = True
