from sqlalchemy import inspect, text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import run_migrations
from app.models import Commission


def test_migration_adds_income_autologged_to_legacy_ledger(legacy_engine):
    run_migrations(legacy_engine)

    with Session(legacy_engine) as session:
        row = session.get(Commission, 1)
    assert row is not None
    assert row.client == "old client"
    assert row.income_autologged is False
    assert row.amount_cents == 20000  # 200.0 dollars converted to cents


def test_migration_is_idempotent(legacy_engine):
    for _ in range(2):
        run_migrations(legacy_engine)

    with Session(legacy_engine) as session:
        row = session.get(Commission, 1)
    assert row is not None and row.income_autologged is False
    assert row.amount_cents == 20000


def test_migrations_record_version_history(legacy_engine):
    run_migrations(legacy_engine)

    with legacy_engine.connect() as conn:
        current = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert current == "0002"


def test_fresh_database_via_migrations_matches_metadata():
    """The baseline migration must produce exactly the schema SQLModel declares."""
    migrated = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    run_migrations(migrated)

    created = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(created)

    def schema(engine):
        inspector = inspect(engine)
        return {
            table: sorted(
                (column["name"], str(column["type"]), column["nullable"]) for column in inspector.get_columns(table)
            )
            for table in inspector.get_table_names()
            if table != "alembic_version"  # Alembic's own bookkeeping table
        }

    assert schema(migrated) == schema(created)
    migrated.dispose()
    created.dispose()
