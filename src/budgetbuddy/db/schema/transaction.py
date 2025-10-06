from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column
from src.budgetbuddy.db.schema.base import ModelBase


class TransactionColumnsMixin:
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)


class Transaction(ModelBase, TransactionColumnsMixin):
    __tablename__ = "transactions"
