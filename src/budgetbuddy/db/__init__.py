"""
Import all models here so that Base.metadata.create_all() picks them up.
"""

from src.budgetbuddy.db.models.transactions import Transaction

__all__ = ["Transaction"]
