from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Commission, Transaction
from app.schemas import CommissionCreate, CommissionRead, CommissionUpdate
from app.services.stats import net_amount

router = APIRouter(prefix="/commissions", tags=["commissions"])


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
        effective_rate=rate,
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


@router.get("", response_model=list[CommissionRead])
def list_commissions(session: Session = Depends(get_session)):
    rows = session.exec(select(Commission).order_by(Commission.created_at.desc())).all()
    return [_to_read(c) for c in rows]


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
    session.commit()
    session.refresh(c)
    return _to_read(c)


@router.patch("/{commission_id}", response_model=CommissionRead)
def update_commission(commission_id: int, payload: CommissionUpdate, session: Session = Depends(get_session)):
    c = _get_or_404(session, commission_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        data["status"] = data["status"].value
    if "transaction_id" in data:
        _validate_transaction_link(session, data["transaction_id"], commission_id=c.id)
    for key, value in data.items():
        setattr(c, key, value)
    session.add(c)
    session.commit()
    session.refresh(c)
    return _to_read(c)


@router.delete("/{commission_id}", status_code=204)
def delete_commission(commission_id: int, session: Session = Depends(get_session)):
    c = _get_or_404(session, commission_id)
    session.delete(c)
    session.commit()
