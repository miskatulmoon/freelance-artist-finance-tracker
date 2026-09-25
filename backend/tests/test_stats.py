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


def test_cashflow_projection_tracks_balance_and_income_steps(session):
    today = date.today()
    session.add(make_tx("income", 1000.0, "comm", source="commission", tx_date=today))
    session.add(make_tx("expense", 600.0, "paper", tx_date=today))
    session.add(make_commission(amount=300.0, expected_date=today + timedelta(days=10), status="agreed"))
    session.commit()
    radar = cashflow_radar(session, today=today)
    proj = radar["projection"]
    assert len(proj) == 31
    assert proj[0]["day"] == 0
    assert proj[0]["balance"] == radar["balance"]  # 400.0
    assert proj[30]["balance"] == radar["projected_balance_30d"]
    # the committed income lands on day 10, lifting the line
    assert proj[10]["balance"] == round(radar["balance"] + 300.0 - radar["burn_per_day"] * 10, 2)
    assert proj[9]["balance"] == round(radar["balance"] - radar["burn_per_day"] * 9, 2)
    assert proj[30]["date"] == (today + timedelta(days=30)).isoformat()
    assert radar["runway_days"] is not None
    assert radar["projected_zero_date"] is None  # still above water at 30d


def test_cashflow_projection_zero_date_when_depleted(session):
    today = date.today()
    session.add(make_tx("income", 200.0, "comm", source="commission", tx_date=today))
    session.add(make_tx("expense", 2000.0, "rent", tx_date=today))
    session.commit()
    radar = cashflow_radar(session, today=today)
    assert radar["projected_balance_30d"] < 0
    assert radar["projected_zero_date"] is not None
    assert radar["projection"][0]["balance"] <= radar["projection"][0]["balance"]  # sanity
    # the depletion date is the first day the cumulative line dips to zero or below
    zero_idx = next(i for i, p in enumerate(radar["projection"]) if p["balance"] <= 0)
    assert radar["projected_zero_date"] == radar["projection"][zero_idx]["date"]


def test_cashflow_projections_are_null_without_spend(session):
    session.add(make_tx("income", 500.0, "comm", source="commission", tx_date=date.today()))
    session.commit()
    radar = cashflow_radar(session)
    assert radar["burn_per_day"] == 0
    assert radar["runway_days"] is None
    assert radar["coverage_pct"] is None
    assert radar["projected_zero_date"] is None
    # no burn means a flat line at the current balance
    assert all(p["balance"] == radar["balance"] for p in radar["projection"])
