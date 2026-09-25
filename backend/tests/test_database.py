from sqlmodel import Session

from app.database import _migrate_commission_columns
from app.models import Commission


def test_migration_adds_income_autologged_to_legacy_ledger(legacy_engine):
    _migrate_commission_columns(legacy_engine)

    with Session(legacy_engine) as session:
        row = session.get(Commission, 1)
    assert row is not None
    assert row.client == "old client"
    assert row.income_autologged is False


def test_migration_is_idempotent(legacy_engine):
    _migrate_commission_columns(legacy_engine)
    _migrate_commission_columns(legacy_engine)

    with Session(legacy_engine) as session:
        row = session.get(Commission, 1)
    assert row is not None and row.income_autologged is False
