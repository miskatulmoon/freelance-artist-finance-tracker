from collections.abc import Generator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlmodel import Session, create_engine

from app.config import get_settings

connect_args = {"check_same_thread": False} if "sqlite" in get_settings().database_url else {}
engine = create_engine(get_settings().database_url, connect_args=connect_args)

BACKEND_DIR = Path(__file__).resolve().parent.parent
BASELINE_REVISION = "0001"
HEAD_REVISION = "0002"


def _alembic_config() -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    return config


def run_migrations(target_engine) -> None:
    """Bring a ledger (fresh or pre-Alembic) up to the latest schema.

    Databases created before Alembic have tables but no `alembic_version`:
    those get the baseline stamped (so 0001 does not try to re-create the
    tables) and are then upgraded, which modernizes the legacy float-dollar
    columns. Fresh databases simply upgrade from the baseline.
    """
    from app import models  # noqa: F401  (register tables on the metadata)

    tables = set(inspect(target_engine).get_table_names())
    config = _alembic_config()
    with target_engine.connect() as conn:
        config.attributes["connection"] = conn
        if tables and "alembic_version" not in tables:
            command.stamp(config, BASELINE_REVISION)
        command.upgrade(config, HEAD_REVISION)


def init_db() -> None:
    run_migrations(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
