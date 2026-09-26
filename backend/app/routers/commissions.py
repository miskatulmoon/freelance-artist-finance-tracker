from datetime import date as DateType

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlmodel import Session, select

from app.database import get_session
from app.models import Commission, CommissionStatus, Source, Transaction
from app.schemas import CommissionCreate, CommissionPage, CommissionRead, CommissionSummary, CommissionUpdate
from app.services.stats import commission_income_summary

router = APIRouter(prefix="/commissions", tags=["commissions"])


def _status_rank():
    return case(
        (Commission.status == CommissionStatus.IN_PROGRESS.value, 0),
        (Commission.status == CommissionStatus.AGREED.value, 1),
        (Commission.status == CommissionStatus.COMPLETED.value, 2),
        (Commission.status == CommissionStatus.CANCELLED.value, 3),
        else_=4,
    )


def _ordered_query():
    return select(Commission).order_by(
        _status_rank().asc(),
        Commission.expected_date.asc().nulls_last(),
        Commission.created_at.desc(),
        Commission.id.desc(),
    )


def _get_or_404(session: Session, commission_id: int) -> Commission:
    c = session.get(Commission, commission_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Commission not found")
    return c


def _validate_transaction_link(session: Session, transaction_id: int | None, commission_id: int | None = None) -> None:
    if transaction_id is None:
        return

    transaction = session.get(Transaction, transaction_id)
    if transaction is None or transaction.type != "income":
        raise HTTPException(status_code=422, detail="transaction_id must reference an income transaction")

    query = select(Commission).where(Commission.transaction_id == transaction_id)
    if commission_id is not None:
        query = query.where(Commission.id != commission_id)
    if session.exec(query).first() is not None:
        raise HTTPException(status_code=422, detail="transaction_id is already linked to a commission")


def _log_completion_income(session: Session, c: Commission) -> None:
    """Write the piece's income into the ledger when it is completed.

    Skips commissions the artist already linked an income slip to, and
    refuses to complete pieces logged without an agreed price.
    """
    if c.transaction_id is not None:
        return
    if c.amount_cents is None:
        raise HTTPException(status_code=422, detail="commission has no agreed price to record as income")

    tx = Transaction(
        type="income",
        amount_cents=c.amount_cents,
        description=f"commission: {c.piece} for {c.client}",
        date=DateType.today(),
        fee_amount_cents=None,
        source=Source.COMMISSION.value,
        category=None,
        merchant=None,
        auto_categorized=False,
    )
    session.add(tx)
    session.flush()
    c.transaction_id = tx.id
    c.income_autologged = True


def _retract_autologged_income(session: Session, c: Commission) -> None:
    """Take the auto-written income slip back out of the ledger.

    Income slips the artist linked by hand are left alone — the tracker
    only retracts what the tracker wrote.
    """
    if not c.income_autologged or c.transaction_id is None:
        return
    tx = session.get(Transaction, c.transaction_id)
    if tx is not None:
        session.delete(tx)
    c.transaction_id = None
    c.income_autologged = False


def _apply_status(session: Session, c: Commission, new_status: str) -> None:
    if c.status == new_status:
        return
    if c.status == CommissionStatus.COMPLETED.value:
        _retract_autologged_income(session, c)
    if new_status == CommissionStatus.COMPLETED.value:
        _log_completion_income(session, c)
    c.status = new_status


@router.get("", response_model=CommissionPage)
def list_commissions(
    status: CommissionStatus | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    base = _ordered_query()
    count_stmt = select(func.count()).select_from(Commission)
    if status is not None:
        base = base.where(Commission.status == status.value)
        count_stmt = count_stmt.where(Commission.status == status.value)
    total = int(session.exec(count_stmt).one() or 0)
    rows = session.exec(base.offset(offset).limit(limit)).all()
    return CommissionPage(
        items=[CommissionRead.from_model(c) for c in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/summary", response_model=CommissionSummary)
def commissions_summary(session: Session = Depends(get_session)):
    return commission_income_summary(session)


@router.post("", response_model=CommissionRead, status_code=201)
def create_commission(payload: CommissionCreate, session: Session = Depends(get_session)):
    _validate_transaction_link(session, payload.transaction_id)
    c = Commission(
        client=payload.client,
        piece=payload.piece,
        hours_spent=payload.hours_spent,
        amount_cents=payload.amount_cents,
        expected_date=payload.expected_date,
        status=payload.status.value,
        transaction_id=payload.transaction_id,
    )
    session.add(c)
    session.flush()
    if c.status == CommissionStatus.COMPLETED.value:
        _log_completion_income(session, c)
    session.commit()
    session.refresh(c)
    return CommissionRead.from_model(c)


@router.patch("/{commission_id}", response_model=CommissionRead)
def update_commission(commission_id: int, payload: CommissionUpdate, session: Session = Depends(get_session)):
    c = _get_or_404(session, commission_id)
    _apply_status(session, c, payload.status.value)
    session.add(c)
    session.commit()
    session.refresh(c)
    return CommissionRead.from_model(c)


@router.delete("/{commission_id}", status_code=204)
def delete_commission(commission_id: int, session: Session = Depends(get_session)):
    c = _get_or_404(session, commission_id)
    _retract_autologged_income(session, c)
    session.delete(c)
    session.commit()
