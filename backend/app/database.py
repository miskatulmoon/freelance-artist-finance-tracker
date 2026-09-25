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


def init_db() -> None:
    from app import models  # noqa: F401  (register tables)

    SQLModel.metadata.create_all(engine)
    _migrate_commission_columns(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
