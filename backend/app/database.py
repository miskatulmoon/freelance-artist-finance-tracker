from collections.abc import Generator

from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

connect_args = {"check_same_thread": False} if "sqlite" in get_settings().database_url else {}
engine = create_engine(get_settings().database_url, connect_args=connect_args)

_COMMISSION_COLUMNS = {
    "income_autologged": "ALTER TABLE commission ADD COLUMN income_autologged BOOLEAN NOT NULL DEFAULT 0",
}


def _migrate_commission_columns(target_engine) -> None:
    """Additive column migrations for older ledgers (SQLite has no Alembic here)."""
    inspector = inspect(target_engine)
    if "commission" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("commission")}
    with target_engine.begin() as conn:
        for name, ddl in _COMMISSION_COLUMNS.items():
            if name not in existing:
                conn.execute(text(ddl))


def _migrate_money_to_cents(target_engine) -> None:
    """Convert legacy float dollar columns to integer cents.

    Older ledgers stored money as float dollars in `amount` / `fee_amount`.
    This adds the `_cents` columns, backfills them, and drops the old ones.
    """
    inspector = inspect(target_engine)
    tables = set(inspector.get_table_names())
    with target_engine.begin() as conn:
        if "transaction" in tables:
            existing = {column["name"] for column in inspector.get_columns("transaction")}
            if "amount" in existing and "amount_cents" not in existing:
                conn.execute(text('ALTER TABLE "transaction" ADD COLUMN amount_cents INTEGER'))
                conn.execute(text('ALTER TABLE "transaction" ADD COLUMN fee_amount_cents INTEGER'))
                conn.execute(text('UPDATE "transaction" SET amount_cents = CAST(ROUND(amount * 100) AS INTEGER)'))
                conn.execute(
                    text(
                        'UPDATE "transaction" SET fee_amount_cents = CAST(ROUND(fee_amount * 100) AS INTEGER) '
                        "WHERE fee_amount IS NOT NULL"
                    )
                )
                conn.execute(text('ALTER TABLE "transaction" DROP COLUMN amount'))
                conn.execute(text('ALTER TABLE "transaction" DROP COLUMN fee_amount'))
        if "commission" in tables:
            existing = {column["name"] for column in inspector.get_columns("commission")}
            if "amount" in existing and "amount_cents" not in existing:
                conn.execute(text("ALTER TABLE commission ADD COLUMN amount_cents INTEGER"))
                conn.execute(
                    text(
                        "UPDATE commission SET amount_cents = CAST(ROUND(amount * 100) AS INTEGER) "
                        "WHERE amount IS NOT NULL"
                    )
                )
                conn.execute(text("ALTER TABLE commission DROP COLUMN amount"))


def init_db() -> None:
    from app import models  # noqa: F401  (register tables)

    SQLModel.metadata.create_all(engine)
    _migrate_commission_columns(engine)
    _migrate_money_to_cents(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
