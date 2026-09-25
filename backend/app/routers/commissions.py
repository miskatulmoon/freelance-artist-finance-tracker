from datetime import date as DateType

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Commission, CommissionStatus, Source, Transaction
from app.schemas import CommissionCreate, CommissionRead, CommissionSummary, CommissionUpdate
from app.services.stats import commission_income_summary, net_amount

router = APIRouter(prefix="/commissions", tags=["commissions"])

_STATUS_ORDER = {
    CommissionStatus.IN_PROGRESS.value: 0,
    CommissionStatus.AGREED.value: 1,
    CommissionStatus.COMPLETED.value: 2,
    CommissionStatus.CANCELLED.value: 3,
}


def _to_read(c: Commission) -> CommissionRead:
    rate = None
    if c.transaction and c.transaction.type == "income" and c.hours_spent > 0:
        rate = round(net_amount(c.transaction) / c.hours_spent, 2)
    return CommissionRead(
        id=c.id,
        client=c.client,
        piece=c.piece,
        hours_spent=c.hours_spent,
        amount=c.amount,
        expected_date=c.expected_date,
        status=c.status,
        transaction_id=c.transaction_id,
        income_autologged=bool(c.income_autologged),
        effective_rate=rate,
    )


def _sort_key(c: Commission) -> tuple:
    rank = _STATUS_ORDER.get(c.status, 4)
    due = (0, c.expected_date.toordinal()) if c.expected_date else (1, 0)
    return (rank, due, -c.created_at.timestamp())


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
    if c.amount is None:
        raise HTTPException(status_code=422, detail="commission has no agreed price to record as income")

    tx = Transaction(
        type="income",
        amount=c.amount,
        description=f"commission: {c.piece} for {c.client}",
        date=DateType.today(),
        fee_amount=None,
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


@router.get("", response_model=list[CommissionRead])
def list_commissions(session: Session = Depends(get_session)):
    rows = session.exec(select(Commission)).all()
    return [_to_read(c) for c in sorted(rows, key=_sort_key)]


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
        amount=payload.amount,
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
    return _to_read(c)


@router.patch("/{commission_id}", response_model=CommissionRead)
def update_commission(commission_id: int, payload: CommissionUpdate, session: Session = Depends(get_session)):
    c = _get_or_404(session, commission_id)
    _apply_status(session, c, payload.status.value)
    session.add(c)
    session.commit()
    session.refresh(c)
    return _to_read(c)


@router.delete("/{commission_id}", status_code=204)
def delete_commission(commission_id: int, session: Session = Depends(get_session)):
    c = _get_or_404(session, commission_id)
    _retract_autologged_income(session, c)
    session.delete(c)
    session.commit()
