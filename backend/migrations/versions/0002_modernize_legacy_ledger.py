"""modernize pre-Alembic ledgers: cents columns + income_autologged

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-25

Brings ledgers created before Alembic up to the current schema:
- `commission.income_autologged` (additive column)
- money stored as integer cents: adds `amount_cents` / `fee_amount_cents`,
  backfills them from the legacy float dollar columns, and drops those columns.

Every step checks for the legacy column first, so this is a no-op on ledgers
already at the current shape (e.g. fresh databases created by 0001).

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _columns(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table)}


def upgrade() -> None:
    if "income_autologged" not in _columns("commission"):
        op.execute("ALTER TABLE commission ADD COLUMN income_autologged BOOLEAN NOT NULL DEFAULT 0")

    transaction_columns = _columns("transaction")
    if "amount" in transaction_columns and "amount_cents" not in transaction_columns:
        op.execute('ALTER TABLE "transaction" ADD COLUMN amount_cents INTEGER')
        op.execute('ALTER TABLE "transaction" ADD COLUMN fee_amount_cents INTEGER')
        op.execute('UPDATE "transaction" SET amount_cents = CAST(ROUND(amount * 100) AS INTEGER)')
        op.execute(
            'UPDATE "transaction" SET fee_amount_cents = CAST(ROUND(fee_amount * 100) AS INTEGER) '
            "WHERE fee_amount IS NOT NULL"
        )
        op.execute('ALTER TABLE "transaction" DROP COLUMN amount')
        op.execute('ALTER TABLE "transaction" DROP COLUMN fee_amount')

    commission_columns = _columns("commission")
    if "amount" in commission_columns and "amount_cents" not in commission_columns:
        op.execute("ALTER TABLE commission ADD COLUMN amount_cents INTEGER")
        op.execute("UPDATE commission SET amount_cents = CAST(ROUND(amount * 100) AS INTEGER) WHERE amount IS NOT NULL")
        op.execute("ALTER TABLE commission DROP COLUMN amount")


def downgrade() -> None:
    # Restoring float dollars loses the cents guarantee; kept for completeness.
    commission_columns = _columns("commission")
    if "amount_cents" in commission_columns and "amount" not in commission_columns:
        op.execute("ALTER TABLE commission ADD COLUMN amount FLOAT")
        op.execute("UPDATE commission SET amount = amount_cents / 100.0 WHERE amount_cents IS NOT NULL")
        op.execute("ALTER TABLE commission DROP COLUMN amount_cents")

    transaction_columns = _columns("transaction")
    if "amount_cents" in transaction_columns and "amount" not in transaction_columns:
        op.execute('ALTER TABLE "transaction" ADD COLUMN amount FLOAT')
        op.execute('ALTER TABLE "transaction" ADD COLUMN fee_amount FLOAT')
        op.execute('UPDATE "transaction" SET amount = amount_cents / 100.0 WHERE amount_cents IS NOT NULL')
        op.execute('UPDATE "transaction" SET fee_amount = fee_amount_cents / 100.0 WHERE fee_amount_cents IS NOT NULL')
        op.execute('ALTER TABLE "transaction" DROP COLUMN amount_cents')
        op.execute('ALTER TABLE "transaction" DROP COLUMN fee_amount_cents')
