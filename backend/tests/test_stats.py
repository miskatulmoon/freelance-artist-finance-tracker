from datetime import date, timedelta

from app.services.stats import (
    balance,
    cashflow_radar,
    committed_income_30d,
    hourly_rate,
    net_amount,
    per_source_net,
    top_merchants,
    total_fees,
)
from tests.conftest import make_commission, make_tx


def test_net_amount_rounds_and_handles_fee():
    tx = make_tx("income", 100.0, "sale", fee=3.333)
    assert net_amount(tx) == 96.67
    assert net_amount(make_tx("expense", 50.0, "x")) == 50.0


def test_balance_subtracts_expenses_from_net_income(session):
    session.add(make_tx("income", 500.0, "commission", source="commission", fee=15.0))
    session.add(make_tx("expense", 60.0, "supplies", category="supplies"))
    session.commit()
    assert balance(session) == 425.0


def test_per_source_net(session):
    session.add(make_tx("income", 300.0, "comm", source="commission"))
    session.add(make_tx("income", 100.0, "etsy", source="etsy", fee=5.0))
    session.commit()
    assert per_source_net(session) == {"commission": 300.0, "etsy": 95.0}


def test_total_fees(session):
    session.add(make_tx("income", 100.0, "etsy", source="etsy", fee=4.0))
    session.add(make_tx("income", 100.0, "etsy", source="etsy", fee=3.0))
    session.commit()
    assert total_fees(session) == 7.0


def test_hourly_rate_uses_linked_income_net(session):
    income = make_tx("income", 500.0, "portrait", source="commission", fee=50.0)
    session.add(income)
    session.commit()
    income_id = income.id
    session.add(make_commission(hours=20.0, amount=500.0, transaction_id=income_id, status="completed"))
    session.add(make_commission(hours=5.0, amount=100.0, status="agreed"))
    session.commit()
    assert hourly_rate(session) == 22.5  # 450 net / 20 hours


def test_hourly_rate_none_without_hours(session):
    assert hourly_rate(session) is None


def test_top_merchants_sorted_desc(session):
    session.add(make_tx("expense", 20.0, "ink", merchant="Blick"))
    session.add(make_tx("expense", 45.0, "tab", merchant="Wacom"))
    session.add(make_tx("expense", 15.0, "paper", merchant="Blick"))
    session.commit()
    top = top_merchants(session)
    assert top[0] == {"merchant": "Wacom", "total": 45.0}
    assert top[1] == {"merchant": "Blick", "total": 35.0}


def test_committed_income_counts_unpaid_commissions_in_window(session):
    today = date.today()
    in_window = make_commission(amount=300.0, expected_date=today + timedelta(days=10), status="agreed")
    too_far = make_commission(amount=400.0, expected_date=today + timedelta(days=60), status="agreed")
    paid = make_commission(amount=250.0, expected_date=today + timedelta(days=5), status="completed")
    paid.transaction_id = 1
    session.add_all([in_window, too_far, paid])
    session.commit()
    assert committed_income_30d(session, today=today) == 300.0


def test_cashflow_radar_low_when_burn_exceeds_resources(session):
    # massive spend in the last 2 days, tiny balance
    session.add(make_tx("expense", 2000.0, "printer", tx_date=date.today()))
    session.commit()
    radar = cashflow_radar(session)
    assert radar["burn_next_30d"] > 0
    assert radar["coverage_pct"] < 100
    assert radar["level"] == "low"
    assert radar["projected_balance_30d"] < 0
