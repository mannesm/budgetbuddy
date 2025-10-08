"""Adapter for converting Bunq SDK objects to domain models."""

from bunq.sdk.model.generated.endpoint import PaymentApiObject
from pydantic import BaseModel
from src.budgetbuddy.schemas.transaction import TransactionCreate


class BunqPaymentAdapter(BaseModel):
    """Adapter to map Bunq Payment objects to TransactionCreate schemas.

    This provides a clean separation between external API and our domain.
    """

    @staticmethod
    def to_transaction_create(payment: PaymentApiObject) -> TransactionCreate:
        """
        Convert a Bunq PaymentApiObject to a TransactionCreate schema.

        Args:
            payment (PaymentApiObject): The Bunq payment object from SDK.

        Returns:
            TransactionCreate: Domain model ready for database insertion.
        """
        amount = float(payment.amount.value) if payment.amount else 0.0
        currency = payment.amount.currency if payment.amount else "EUR"
        alias = getattr(payment, "counterparty_alias", None)
        label = getattr(alias, "label_monetary_account", None) if alias else None

        if label:
            counterparty_name = getattr(label, "display_name", None)
            counterparty_iban = getattr(label, "iban", None)
        else:
            counterparty_name = getattr(alias, "display_name", None) if alias else None
            counterparty_iban = getattr(alias, "iban", None) if alias else None

        return TransactionCreate(
            amount=abs(amount),
            currency=currency,
            description=payment.description if payment.description else None,
            transaction_type=payment.type_ if hasattr(payment, "type_") else None,
            counterparty_name=counterparty_name,
            counterparty_iban=counterparty_iban,
            external_source="bunq",
            external_id=f"bunq_{payment.id_}",
            external_created_at=payment.created if hasattr(payment, "created") else None,
            external_updated_at=payment.updated if hasattr(payment, "updated") else None,
            category=None,
            tags=None,
            notes=None,
        )

    @staticmethod
    def to_transaction_creates(payments: list[PaymentApiObject]) -> list[TransactionCreate]:
        """Convert multiple Bunq payments to TransactionCreate schemas.

        Args:
            payments (list[PaymentApiObject]): List of Bunq payment objects.

        Returns:
            list[TransactionCreate]: List of domain models.
        """
        return [BunqPaymentAdapter.to_transaction_create(p) for p in payments]
