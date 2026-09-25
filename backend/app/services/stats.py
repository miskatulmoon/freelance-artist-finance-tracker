from datetime import date as DateType
from datetime import timedelta

from sqlmodel import Session, select

from app.models import Commission, CommissionStatus, Source, Transaction


def net_amount(tx: Transaction) -> float:
    return round(tx.amount - (tx.fee_amount or 0.0), 2)


def _sum(values: list[float | None]) -> float:
    return round(sum(v or 0.0 for v in values), 2)


def income_rows(session: Session) -> list[Transaction]:
    return list(session.exec(select(Transaction).where(Transaction.type == "income")).all())


def expense_rows(session: Session) -> list[Transaction]:
    return list(session.exec(select(Transaction).where(Transaction.type == "expense")).all())


def balance(session: Session) -> float:
    return round(sum(net_amount(t) for t in income_rows(session)) - sum(t.amount for t in expense_rows(session)), 2)


def per_source_net(session: Session) -> dict[str, float]:
    totals: dict[str, float] = {}
    for t in income_rows(session):
        source = t.source or Source.OTHER_INCOME.value
        totals[source] = round(totals.get(source, 0.0) + net_amount(t), 2)
    return totals


def monthly_trend(session: Session, months: int = 6) -> list[dict]:
    cutoff = (DateType.today().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(weeks=4 * (months - 1))
    buckets: dict[str, dict] = {}
    for t in list(session.exec(select(Transaction).where(Transaction.date >= cutoff)).all()):
        key = t.date.strftime("%Y-%m")
        bucket = buckets.setdefault(key, {"month": key, "income": 0.0, "expense": 0.0, "net": 0.0})
        if t.type == "income":
            bucket["income"] = round(bucket["income"] + net_amount(t), 2)
        else:
            bucket["expense"] = round(bucket["expense"] + t.amount, 2)
        bucket["net"] = round(bucket["income"] - bucket["expense"], 2)
    return [buckets[k] for k in sorted(buckets)]


def top_merchants(session: Session, limit: int = 5) -> list[dict]:
    totals: dict[str, float] = {}
    for t in expense_rows(session):
        merchant = (t.merchant or "unknown").strip()
        totals[merchant] = round(totals.get(merchant, 0.0) + t.amount, 2)
    return [{"merchant": m, "total": totals[m]} for m in sorted(totals, key=lambda m: -totals[m])[:limit]]


def total_fees(session: Session) -> float:
    return _sum(t.fee_amount for t in income_rows(session) if t.fee_amount)


def hourly_rate(session: Session) -> float | None:
    commissions = session.exec(
        select(Commission).where(
            Commission.transaction_id.is_not(None), Commission.status != CommissionStatus.CANCELLED.value
        )
    ).all()
    income = 0.0
    hours = 0.0
    for c in commissions:
        linked = c.transaction
        if linked and linked.type == "income":
            income += net_amount(linked)
            hours += c.hours_spent
    if hours <= 0:
        return None
    return round(income / hours, 2)


def burn_rate(session: Session, days: int = 60) -> float:
    cutoff = DateType.today() - timedelta(days=days)
    spent = sum(
        t.amount
        for t in session.exec(
            select(Transaction).where(Transaction.type == "expense", Transaction.date >= cutoff)
        ).all()
    )
    return round(spent / days, 2)


def committed_income_30d(session: Session, today: DateType | None = None) -> float:
    today = today or DateType.today()
    return round(sum(c.amount for c in _committed_income_rows(session, today)), 2)


def _committed_income_rows(session: Session, today: DateType) -> list[Commission]:
    horizon = today + timedelta(days=30)
    rows = session.exec(
        select(Commission).where(
            Commission.status.in_([CommissionStatus.AGREED.value, CommissionStatus.IN_PROGRESS.value]),
            Commission.expected_date.is_not(None),
            Commission.transaction_id.is_(None),
        )
    ).all()
    return [c for c in rows if c.expected_date and today <= c.expected_date <= horizon and c.amount]


def _projection_series(
    balance_now: float,
    burn_per_day: float,
    committed_rows: list[Commission],
    today: DateType,
    days: int = 30,
) -> list[dict]:
    committed = [c for c in committed_rows if c.expected_date is not None]
    points: list[dict] = []
    for d in range(days + 1):
        day_date = today + timedelta(days=d)
        landed = sum(c.amount for c in committed if c.expected_date <= day_date)
        points.append(
            {
                "day": d,
                "date": day_date.isoformat(),
                "balance": round(balance_now + landed - round(burn_per_day * d, 2), 2),
            }
        )
    return points


def cashflow_radar(session: Session, today: DateType | None = None) -> dict:
    today = today or DateType.today()
    balance_now = balance(session)
    burn_per_day = burn_rate(session)
    burn_30d = round(burn_per_day * 30, 2)
    committed_rows = _committed_income_rows(session, today)
    committed = round(sum(c.amount for c in committed_rows), 2)
    projected = round(balance_now + committed - burn_30d, 2)
    coverage = round((balance_now + committed) / burn_30d * 100, 1) if burn_30d > 0 else None

    if coverage is None:
        level = "unknown"
    elif coverage >= 130:
        level = "healthy"
    elif coverage >= 100:
        level = "moderate"
    else:
        level = "low"

    runway_days = round((balance_now + committed) / burn_per_day, 1) if burn_per_day > 0 else None
    projection = _projection_series(balance_now, burn_per_day, committed_rows, today)
    zero_point = next((p for p in projection if p["balance"] <= 0), None)
    projected_zero_date = zero_point["date"] if zero_point else None

    return {
        "balance": balance_now,
        "burn_per_day": burn_per_day,
        "burn_next_30d": burn_30d,
        "committed_next_30d": committed,
        "projected_balance_30d": projected,
        "coverage_pct": coverage,
        "level": level,
        "as_of": today.isoformat(),
        "projection": projection,
        "runway_days": runway_days,
        "projected_zero_date": projected_zero_date,
    }


def context_bundle(session: Session) -> dict:
    return {
        "balance": balance(session),
        "per_source_net": per_source_net(session),
        "monthly_trend": monthly_trend(session),
        "top_merchants": top_merchants(session),
        "total_fees": total_fees(session),
        "hourly_rate": hourly_rate(session),
        "cashflow": cashflow_radar(session),
    }
