from datetime import date as DateType
from datetime import timedelta

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Commission, CommissionStatus, Source, Transaction, cents_to_dollars


def net_amount_cents(tx: Transaction) -> int:
    return tx.amount_cents - (tx.fee_amount_cents or 0)


def net_amount(tx: Transaction) -> float:
    return cents_to_dollars(net_amount_cents(tx))


def income_rows(session: Session) -> list[Transaction]:
    """Legacy helper kept for backwards compatibility.

    Aggregations below no longer use this (they run SUM/GROUP BY in SQL so
    dashboard loads stay constant-time in Python). Prefer the aggregate
    functions directly for new code.
    """
    return list(session.exec(select(Transaction).where(Transaction.type == "income")).all())


def expense_rows(session: Session) -> list[Transaction]:
    """Legacy helper kept for backwards compatibility (see income_rows)."""
    return list(session.exec(select(Transaction).where(Transaction.type == "expense")).all())


def _income_net_cents(session: Session) -> int:
    stmt = select(func.sum(Transaction.amount_cents - func.coalesce(Transaction.fee_amount_cents, 0))).where(
        Transaction.type == "income"
    )
    return int(session.exec(stmt).one() or 0)


def _expense_cents(session: Session, cutoff: DateType | None = None) -> int:
    stmt = select(func.sum(Transaction.amount_cents)).where(Transaction.type == "expense")
    if cutoff is not None:
        stmt = stmt.where(Transaction.date >= cutoff)
    return int(session.exec(stmt).one() or 0)


def balance(session: Session) -> float:
    return cents_to_dollars(_income_net_cents(session) - _expense_cents(session))


def per_source_net(session: Session) -> dict[str, float]:
    stmt = (
        select(
            Transaction.source,
            func.sum(Transaction.amount_cents - func.coalesce(Transaction.fee_amount_cents, 0)),
        )
        .where(Transaction.type == "income")
        .group_by(Transaction.source)
    )
    totals: dict[str, int] = {}
    for raw_source, total in session.exec(stmt).all():
        key = raw_source or Source.OTHER_INCOME.value
        totals[key] = totals.get(key, 0) + int(total or 0)
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

    month_expr = func.strftime("%Y-%m", Transaction.date).label("month")
    stmt = (
        select(
            month_expr,
            Transaction.type,
            func.sum(Transaction.amount_cents).label("gross_cents"),
            func.sum(func.coalesce(Transaction.fee_amount_cents, 0)).label("fee_cents"),
        )
        .where(Transaction.date >= cutoff)
        .group_by(month_expr, Transaction.type)
    )
    for month_key, tx_type, gross_cents, fee_cents in session.exec(stmt).all():
        if month_key not in buckets:
            continue
        bucket = buckets[month_key]
        if tx_type == "income":
            bucket["income"] += int(gross_cents or 0) - int(fee_cents or 0)
        else:
            bucket["expense"] += int(gross_cents or 0)
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
    merchant_expr = func.trim(func.coalesce(Transaction.merchant, "")).label("merchant")
    stmt = (
        select(merchant_expr, func.sum(Transaction.amount_cents).label("total_cents"))
        .where(Transaction.type == "expense")
        .group_by(merchant_expr)
    )
    totals: dict[str, int] = {}
    for raw_merchant, total_cents in session.exec(stmt).all():
        name = (raw_merchant or "").strip() or "unknown"
        totals[name] = totals.get(name, 0) + int(total_cents or 0)
    ranked = sorted(totals, key=lambda m: -totals[m])[:limit]
    return [{"merchant": m, "total": cents_to_dollars(totals[m])} for m in ranked]


def total_fees(session: Session) -> float:
    stmt = select(func.sum(Transaction.fee_amount_cents)).where(
        Transaction.type == "income", Transaction.fee_amount_cents.is_not(None)
    )
    return cents_to_dollars(int(session.exec(stmt).one() or 0))


def hourly_rate(session: Session) -> float | None:
    stmt = (
        select(
            func.sum(Transaction.amount_cents - func.coalesce(Transaction.fee_amount_cents, 0)),
            func.sum(Commission.hours_spent),
        )
        .select_from(Commission)
        .join(Transaction, Transaction.id == Commission.transaction_id)
        .where(
            Commission.transaction_id.is_not(None),
            Commission.status != CommissionStatus.CANCELLED.value,
            Transaction.type == "income",
        )
    )
    income_cents, hours = session.exec(stmt).one()
    hours = float(hours or 0)
    if hours <= 0:
        return None
    return round(cents_to_dollars(int(income_cents or 0)) / hours, 2)


def commission_income_summary(session: Session) -> dict:
    """Income by commission status: what's on the desk vs. earned vs. lost."""
    stmt = select(
        Commission.status,
        func.count().label("n"),
        func.sum(Commission.amount_cents).label("total_cents"),
    ).group_by(Commission.status)
    earned = 0
    expected = 0
    lost = 0
    counts = {s.value: 0 for s in CommissionStatus}
    active = 0
    for status, count, total_cents in session.exec(stmt).all():
        if status not in counts:
            continue
        counts[status] += int(count or 0)
        if total_cents is None:
            continue
        amount_cents = int(total_cents)
        if status == CommissionStatus.COMPLETED.value:
            earned += amount_cents
        elif status in (CommissionStatus.AGREED.value, CommissionStatus.IN_PROGRESS.value):
            expected += amount_cents
            active += 1
        elif status == CommissionStatus.CANCELLED.value:
            lost += amount_cents
    return {
        "expected_income": cents_to_dollars(expected),
        "earned_income": cents_to_dollars(earned),
        "lost_income": cents_to_dollars(lost),
        "counts": counts,
        "active_count": active,
    }


def burn_rate(session: Session, days: int = 60) -> float:
    cutoff = DateType.today() - timedelta(days=days)
    spent_cents = _expense_cents(session, cutoff=cutoff)
    return round(cents_to_dollars(spent_cents) / days, 2)


def committed_income_30d(session: Session, today: DateType | None = None) -> float:
    today = today or DateType.today()
    horizon = today + timedelta(days=30)
    stmt = select(func.sum(Commission.amount_cents)).where(
        Commission.status.in_([CommissionStatus.AGREED.value, CommissionStatus.IN_PROGRESS.value]),
        Commission.expected_date.is_not(None),
        Commission.transaction_id.is_(None),
        Commission.amount_cents.is_not(None),
        Commission.expected_date >= today,
        Commission.expected_date <= horizon,
    )
    return cents_to_dollars(int(session.exec(stmt).one() or 0))


def _committed_income_rows(session: Session, today: DateType) -> list[Commission]:
    horizon = today + timedelta(days=30)
    return list(
        session.exec(
            select(Commission).where(
                Commission.status.in_([CommissionStatus.AGREED.value, CommissionStatus.IN_PROGRESS.value]),
                Commission.expected_date.is_not(None),
                Commission.transaction_id.is_(None),
                Commission.amount_cents.is_not(None),
                Commission.expected_date >= today,
                Commission.expected_date <= horizon,
            )
        ).all()
    )


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
    balance_now_cents = _income_net_cents(session) - _expense_cents(session)
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
