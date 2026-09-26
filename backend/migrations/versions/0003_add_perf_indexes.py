"""add perf indexes for stats aggregations

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-26

Aggregations in app/services/stats.py filter/group by type, date, source,
merchant, status, and expected_date. Without indexes every dashboard load
is a full-table scan. This adds single-column + composite indexes; each
step is a no-op if the index already exists (e.g. fresh test DBs built
with SQLModel metadata).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES: list[tuple[str, str, list[str]]] = [
    ("ix_transaction_type", "transaction", ["type"]),
    ("ix_transaction_date", "transaction", ["date"]),
    ("ix_transaction_source", "transaction", ["source"]),
    ("ix_transaction_merchant", "transaction", ["merchant"]),
    ("ix_transaction_type_date", "transaction", ["type", "date"]),
    ("ix_commission_status", "commission", ["status"]),
    ("ix_commission_expected_date", "commission", ["expected_date"]),
    ("ix_commission_status_expected_date", "commission", ["status", "expected_date"]),
]


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _existing_indexes(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    return {index["name"] for index in inspector.get_indexes(table)}


def upgrade() -> None:
    tables = _tables()
    for name, table, columns in INDEXES:
        if table not in tables:
            continue
        if name not in _existing_indexes(table):
            op.create_index(name, table, columns)


def downgrade() -> None:
    for name, table, _columns in reversed(INDEXES):
        if name in _existing_indexes(table):
            op.drop_index(name, table_name=table)
