from datetime import date as DateType
from datetime import timedelta

from sqlmodel import Session, select

from app.models import Commission, CommissionStatus, Source, Transaction, cents_to_dollars


def net_amount_cents(tx: Transaction) -> int:
    return tx.amount_cents - (tx.fee_amount_cents or 0)


def net_amount(tx: Transaction) -> float:
    return cents_to_dollars(net_amount_cents(tx))


def _sum_cents(values: list[int | None]) -> float:
    return cents_to_dollars(sum(v or 0 for v in values))


def income_rows(session: Session) -> list[Transaction]:
    return list(session.exec(select(Transaction).where(Transaction.type == "income")).all())


def expense_rows(session: Session) -> list[Transaction]:
    return list(session.exec(select(Transaction).where(Transaction.type == "expense")).all())


def balance(session: Session) -> float:
    net_income = sum(net_amount_cents(t) for t in income_rows(session))
    expenses = sum(t.amount_cents for t in expense_rows(session))
    return cents_to_dollars(net_income - expenses)


def per_source_net(session: Session) -> dict[str, float]:
    totals: dict[str, int] = {}
    for t in income_rows(session):
        source = t.source or Source.OTHER_INCOME.value
        totals[source] = totals.get(source, 0) + net_amount_cents(t)
    return {source: cents_to_dollars(cents) for source, cents in totals.items()}


def monthly_trend(session: Session, months: int = 6) -> list[dict]:
    today = DateType.today()
    month_keys: list[str] = []
    buckets: dict[str, dict] = {}
    for delta in range(months - 1, -1, -1):
        y = today.year
        m = today.month - delta
        while m <= 0:
            m += 12
            y -= 1
        while m > 12:
            m -= 12
            y += 1
        key = f"{y:04d}-{m:02d}"
        month_keys.append(key)
        buckets[key] = {"month": key, "income": 0, "expense": 0}

    year, month = map(int, month_keys[0].split("-"))
    cutoff = DateType(year, month, 1)

    for t in list(session.exec(select(Transaction).where(Transaction.date >= cutoff)).all()):
        key = t.date.strftime("%Y-%m")
        if key not in buckets:
            continue
        bucket = buckets[key]
        if t.type == "income":
            bucket["income"] += net_amount_cents(t)
        else:
            bucket["expense"] += t.amount_cents
    return [
        {
            "month": buckets[k]["month"],
            "income": cents_to_dollars(buckets[k]["income"]),
            "expense": cents_to_dollars(buckets[k]["expense"]),
            "net": cents_to_dollars(buckets[k]["income"] - buckets[k]["expense"]),
        }
        for k in month_keys
    ]


def top_merchants(session: Session, limit: int = 5) -> list[dict]:
    totals: dict[str, int] = {}
    for t in expense_rows(session):
        merchant = (t.merchant or "unknown").strip()
        totals[merchant] = totals.get(merchant, 0) + t.amount_cents
    return [
        {"merchant": m, "total": cents_to_dollars(totals[m])} for m in sorted(totals, key=lambda m: -totals[m])[:limit]
    ]


def total_fees(session: Session) -> float:
    return _sum_cents([t.fee_amount_cents for t in income_rows(session) if t.fee_amount_cents])


def hourly_rate(session: Session) -> float | None:
    commissions = session.exec(
        select(Commission).where(
            Commission.transaction_id.is_not(None), Commission.status != CommissionStatus.CANCELLED.value
        )
    ).all()
    income_cents = 0
    hours = 0.0
    for c in commissions:
        linked = c.transaction
        if linked and linked.type == "income":
            income_cents += net_amount_cents(linked)
            hours += c.hours_spent
    if hours <= 0:
        return None
    return round(cents_to_dollars(income_cents) / hours, 2)


def commission_income_summary(session: Session) -> dict:
    """Income by commission status: what's on the desk vs. earned vs. lost."""
    earned = 0
    expected = 0
    lost = 0
    counts = {s.value: 0 for s in CommissionStatus}
    active = 0
    for c in session.exec(select(Commission)).all():
        if c.status not in counts:
            continue
        counts[c.status] += 1
        if c.amount_cents is None:
            continue
        if c.status == CommissionStatus.COMPLETED.value:
            earned += c.amount_cents
        elif c.status in (CommissionStatus.AGREED.value, CommissionStatus.IN_PROGRESS.value):
            expected += c.amount_cents
            active += 1
        elif c.status == CommissionStatus.CANCELLED.value:
            lost += c.amount_cents
    return {
        "expected_income": cents_to_dollars(expected),
        "earned_income": cents_to_dollars(earned),
        "lost_income": cents_to_dollars(lost),
        "counts": counts,
        "active_count": active,
    }


def burn_rate(session: Session, days: int = 60) -> float:
    cutoff = DateType.today() - timedelta(days=days)
    spent_cents = sum(
        t.amount_cents
        for t in session.exec(
            select(Transaction).where(Transaction.type == "expense", Transaction.date >= cutoff)
        ).all()
    )
    return round(cents_to_dollars(spent_cents) / days, 2)


def committed_income_30d(session: Session, today: DateType | None = None) -> float:
    today = today or DateType.today()
    return cents_to_dollars(sum(c.amount_cents for c in _committed_income_rows(session, today)))


def _committed_income_rows(session: Session, today: DateType) -> list[Commission]:
    horizon = today + timedelta(days=30)
    rows = session.exec(
        select(Commission).where(
            Commission.status.in_([CommissionStatus.AGREED.value, CommissionStatus.IN_PROGRESS.value]),
            Commission.expected_date.is_not(None),
            Commission.transaction_id.is_(None),
        )
    ).all()
    return [c for c in rows if c.expected_date and today <= c.expected_date <= horizon and c.amount_cents]


def _projection_series(
    balance_now_cents: int,
    burn_per_day_cents: float,
    committed_rows: list[Commission],
    today: DateType,
    days: int = 30,
) -> list[dict]:
    committed = [c for c in committed_rows if c.expected_date is not None]
    points: list[dict] = []
    for d in range(days + 1):
        day_date = today + timedelta(days=d)
        landed = sum(c.amount_cents for c in committed if c.expected_date <= day_date)
        points.append(
            {
                "day": d,
                "date": day_date.isoformat(),
                "balance": cents_to_dollars(round(balance_now_cents + landed - burn_per_day_cents * d)),
            }
        )
    return points


def cashflow_radar(session: Session, today: DateType | None = None) -> dict:
    today = today or DateType.today()
    balance_now_cents = sum(net_amount_cents(t) for t in income_rows(session)) - sum(
        t.amount_cents for t in expense_rows(session)
    )
    burn_per_day_cents = burn_rate(session) * 100
    burn_30d_cents = burn_per_day_cents * 30
    committed_rows = _committed_income_rows(session, today)
    committed_cents = sum(c.amount_cents for c in committed_rows)
    balance_now = cents_to_dollars(balance_now_cents)
    burn_per_day = cents_to_dollars(round(burn_per_day_cents))
    burn_30d = cents_to_dollars(round(burn_30d_cents))
    committed = cents_to_dollars(committed_cents)
    projected = cents_to_dollars(round(balance_now_cents + committed_cents - burn_30d_cents))
    coverage = round((balance_now_cents + committed_cents) / burn_30d_cents * 100, 1) if burn_30d_cents > 0 else None

    if coverage is None:
        level = "unknown"
    elif coverage >= 130:
        level = "healthy"
    elif coverage >= 100:
        level = "moderate"
    else:
        level = "low"

    runway_days = (
        round((balance_now_cents + committed_cents) / burn_per_day_cents, 1) if burn_per_day_cents > 0 else None
    )
    projection = _projection_series(balance_now_cents, burn_per_day_cents, committed_rows, today)
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
        "commission_summary": commission_income_summary(session),
        "cashflow": cashflow_radar(session),
    }
