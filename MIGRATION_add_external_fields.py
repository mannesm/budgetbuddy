"""Add external fields and metadata to transactions.

Revision ID: add_external_fields
Revises:
Create Date: 2025-10-07

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "add_external_fields"
down_revision = None  # Update this to your latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new fields to transactions table for external source tracking and metadata."""
    # Add transaction metadata columns
    op.add_column(
        "transactions", sa.Column("transaction_type", sa.String(length=50), nullable=True), schema="budgetbuddy"
    )
    op.add_column(
        "transactions", sa.Column("counterparty_name", sa.String(length=255), nullable=True), schema="budgetbuddy"
    )
    op.add_column(
        "transactions", sa.Column("counterparty_iban", sa.String(length=34), nullable=True), schema="budgetbuddy"
    )

    # Add external system tracking columns
    op.add_column(
        "transactions", sa.Column("external_source", sa.String(length=50), nullable=True), schema="budgetbuddy"
    )
    op.add_column("transactions", sa.Column("external_id", sa.String(length=255), nullable=True), schema="budgetbuddy")
    op.add_column(
        "transactions",
        sa.Column("external_created_at", sa.DateTime(timezone=True), nullable=True),
        schema="budgetbuddy",
    )
    op.add_column(
        "transactions",
        sa.Column("external_updated_at", sa.DateTime(timezone=True), nullable=True),
        schema="budgetbuddy",
    )

    # Add user metadata columns
    op.add_column("transactions", sa.Column("category", sa.String(length=100), nullable=True), schema="budgetbuddy")
    op.add_column("transactions", sa.Column("tags", sa.String(), nullable=True), schema="budgetbuddy")
    op.add_column("transactions", sa.Column("notes", sa.String(), nullable=True), schema="budgetbuddy")

    # Create unique index on external_id for idempotency
    op.create_index(
        "ix__budgetbuddy_transactions_external_id", "transactions", ["external_id"], unique=True, schema="budgetbuddy"
    )


def downgrade() -> None:
    """Remove the added columns and index."""
    op.drop_index("ix__budgetbuddy_transactions_external_id", table_name="transactions", schema="budgetbuddy")

    op.drop_column("transactions", "notes", schema="budgetbuddy")
    op.drop_column("transactions", "tags", schema="budgetbuddy")
    op.drop_column("transactions", "category", schema="budgetbuddy")
    op.drop_column("transactions", "external_updated_at", schema="budgetbuddy")
    op.drop_column("transactions", "external_created_at", schema="budgetbuddy")
    op.drop_column("transactions", "external_id", schema="budgetbuddy")
    op.drop_column("transactions", "external_source", schema="budgetbuddy")
    op.drop_column("transactions", "counterparty_iban", schema="budgetbuddy")
    op.drop_column("transactions", "counterparty_name", schema="budgetbuddy")
    op.drop_column("transactions", "transaction_type", schema="budgetbuddy")
