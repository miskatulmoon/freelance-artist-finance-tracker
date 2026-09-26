"""Scale regression tests for stats aggregations.

Before the fix, every dashboard load pulled ALL transactions into Python
(full-table scans + per-row loops). These tests pin the new behavior:
aggregations run as indexed SUM/GROUP BY queries, so 10k rows stay fast
and issue a bounded number of statements.
"""

import time
from datetime import date, timedelta

from sqlalchemy import event, inspect
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine

from app.database import run_migrations
from app.services.stats import cashflow_radar, context_bundle
from tests.conftest import make_tx

EXPECTED_INDEXES = {
    "transaction": {
        "ix_transaction_type",
        "ix_transaction_date",
        "ix_transaction_source",
        "ix_transaction_merchant",
        "ix_transaction_type_date",
    },
    "commission": {
        "ix_commission_status",
        "ix_commission_expected_date",
        "ix_commission_status_expected_date",
    },
}


def test_create_all_declares_perf_indexes(engine):
    for table, expected in EXPECTED_INDEXES.items():
        actual = {index["name"] for index in inspect(engine).get_indexes(table)}
        assert expected <= actual, f"{table} missing indexes: {expected - actual}"


def test_migrated_database_has_perf_indexes():
    migrated = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    run_migrations(migrated)
    try:
        for table, expected in EXPECTED_INDEXES.items():
            actual = {index["name"] for index in inspect(migrated).get_indexes(table)}
            assert expected <= actual, f"migrated {table} missing: {expected - actual}"
    finally:
        migrated.dispose()


def test_dashboard_aggregations_scale_to_10k_rows(session, engine):
    today = date.today()
    rows = []
    for i in range(10_000):
        if i % 2 == 0:
            rows.append(
                make_tx(
                    "income",
                    100.0 + (i % 50),
                    f"sale {i}",
                    tx_date=today - timedelta(days=i % 170),
                    fee=2.0,
                    source="etsy" if i % 4 == 0 else "commission",
                )
            )
        else:
            rows.append(
                make_tx(
                    "expense",
                    20.0 + (i % 30),
                    f"supply {i}",
                    tx_date=today - timedelta(days=i % 170),
                    category="supplies",
                    merchant=f"merchant-{i % 25}",
                )
            )
    session.add_all(rows)
    session.commit()

    queries: list[str] = []

    def count_queries(conn, clause, *args):
        queries.append(str(clause))

    event.listen(engine, "before_cursor_execute", count_queries)
    try:
        start = time.perf_counter()
        bundle = context_bundle(session)
        radar = cashflow_radar(session)
        elapsed = time.perf_counter() - start
    finally:
        event.remove(engine, "before_cursor_execute", count_queries)

    # Correctness spot-checks on the seeded data.
    assert bundle["balance"] == radar["balance"]
    assert set(bundle["per_source_net"]) == {"etsy", "commission"}
    assert len(bundle["monthly_trend"]) == 6
    assert len(bundle["top_merchants"]) == 5
    assert bundle["total_fees"] == 5000 * 2.0

    # Scale assertions: bounded queries (no per-row round-trips) + wall time.
    assert len(queries) <= 25, f"too many statements for one bundle: {len(queries)}"
    assert elapsed < 2.0, f"context_bundle + radar took {elapsed:.2f}s for 10k rows"
