from src.budgetbuddy.banking.bunq.fetch import fetch_all_payments
from src.budgetbuddy.banking.schemas.transaction import BunqPayment
from src.budgetbuddy.services.transaction_service import create_transaction
from src.common.log.logger import get_logger
from src.db import SessionLocal

logger = get_logger(__name__)

logger.debug("Starting to fetch and store Bunq payments")
all_payments = fetch_all_payments(ma_status_filter="ACTIVE")

payment_objects = []
for payment in all_payments:
    logger.debug(f"Fetching payment {payment.id_}")
    bunq_payment = BunqPayment(
        id=int(payment.id_),
        created=payment.created if payment.created else None,
        updated=payment.updated if payment.updated else None,
        amount=float(payment.amount.value) if payment.amount else None,
        currency=payment.amount.currency if payment.amount else None,
        description=payment.description,
        counterparty_name=payment.counterparty_alias.label_monetary_account.display_name
        if payment.counterparty_alias
        else None,
        type=payment.type_,
    )
    payment_objects.append(bunq_payment)
    logger.debug(f"Storing payment {payment.id_}")

for bunq_payment in payment_objects:
    transaction_create = bunq_payment.to_transaction_create()
    with SessionLocal() as session:
        db_transaction = create_transaction(session, transaction_create.model_dump())
        session.commit()
