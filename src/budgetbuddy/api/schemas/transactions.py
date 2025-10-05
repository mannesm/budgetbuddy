from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    description: Optional[str] = None


class TransactionRead(BaseModel):
    itemid: UUID
    createdtimestamp: datetime
    updatedtimestamp: datetime
    amount: float
    currency: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
