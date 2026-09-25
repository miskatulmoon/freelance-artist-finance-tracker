from sqlmodel import Session

from app.database import _migrate_commission_columns, _migrate_money_to_cents
from app.models import Commission


def test_migration_adds_income_autologged_to_legacy_ledger(legacy_engine):
    _migrate_commission_columns(legacy_engine)
    _migrate_money_to_cents(legacy_engine)

    with Session(legacy_engine) as session:
        row = session.get(Commission, 1)
    assert row is not None
    assert row.client == "old client"
    assert row.income_autologged is False
    assert row.amount_cents == 20000  # 200.0 dollars converted to cents


def test_migration_is_idempotent(legacy_engine):
    for _ in range(2):
        _migrate_commission_columns(legacy_engine)
        _migrate_money_to_cents(legacy_engine)

    with Session(legacy_engine) as session:
        row = session.get(Commission, 1)
    assert row is not None and row.income_autologged is False
    assert row.amount_cents == 20000
