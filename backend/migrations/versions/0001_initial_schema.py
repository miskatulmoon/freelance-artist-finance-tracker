"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-25 17:16:37.213994

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("fee_amount_cents", sa.Integer(), nullable=True),
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("merchant", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("auto_categorized", sa.Boolean(), nullable=False),
        sa.Column("created_at", sqlmodel.sql.sqltypes.UTCDateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "commission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("piece", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("hours_spent", sa.Float(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=True),
        sa.Column("expected_date", sa.Date(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("income_autologged", sa.Boolean(), nullable=False),
        sa.Column("created_at", sqlmodel.sql.sqltypes.UTCDateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transaction.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )


def downgrade() -> None:
    op.drop_table("commission")
    op.drop_table("transaction")
