from datetime import date as DateType

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionRead, TransactionUpdate, validate_transaction_fields
from app.services.llm import LLMClient, get_llm
from app.services.stats import net_amount

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _to_read(tx: Transaction) -> TransactionRead:
    return TransactionRead(
        id=tx.id,
        type=tx.type,
        amount=round(tx.amount, 2),
        net_amount=None if tx.type == "expense" else net_amount(tx),
        description=tx.description,
        date=tx.date,
        fee_amount=tx.fee_amount,
        source=tx.source,
        category=tx.category,
        merchant=tx.merchant,
        auto_categorized=tx.auto_categorized,
    )


def _categorize(tx: Transaction, llm: LLMClient) -> None:
    result = llm.categorize(type=tx.type, description=tx.description, merchant=tx.merchant or "", amount=tx.amount)
    if tx.type == "income" and "source" in result:
        tx.source = result["source"]
    elif tx.type == "expense" and "category" in result:
        tx.category = result["category"]
    tx.auto_categorized = True


def _get_or_404(session: Session, transaction_id: int) -> Transaction:
    tx = session.get(Transaction, transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    source: str | None = None,
    category: str | None = None,
    type: str | None = None,
    from_date: DateType | None = None,
    to_date: DateType | None = None,
    session: Session = Depends(get_session),
):
    query = select(Transaction)
    if source:
        query = query.where(Transaction.source == source)
    if category:
        query = query.where(Transaction.category == category)
    if type:
        query = query.where(Transaction.type == type)
    if from_date:
        query = query.where(Transaction.date >= from_date)
    if to_date:
        query = query.where(Transaction.date <= to_date)
    rows = session.exec(query.order_by(Transaction.date.desc(), Transaction.id.desc())).all()
    return [_to_read(tx) for tx in rows]


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(
    payload: TransactionCreate, session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)
):
    tx = Transaction(
        type=payload.type,
        amount=payload.amount,
        description=payload.description,
        date=payload.date,
        fee_amount=payload.fee_amount,
        merchant=payload.merchant,
    )
    if payload.type == "income":
        tx.source = payload.source.value if payload.source else None
    else:
        tx.category = payload.category.value if payload.category else None

    needs_categorization = (payload.type == "income" and tx.source is None) or (
        payload.type == "expense" and tx.category is None
    )
    if needs_categorization:
        _categorize(tx, llm)

    session.add(tx)
    session.commit()
    session.refresh(tx)
    return _to_read(tx)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, payload: TransactionUpdate, session: Session = Depends(get_session)):
    tx = _get_or_404(session, transaction_id)
    data = payload.model_dump(exclude_unset=True)
    if "source" in data:
        data["source"] = data["source"].value if data["source"] else None
    if "category" in data:
        data["category"] = data["category"].value if data["category"] else None
    try:
        validate_transaction_fields(
            tx.type,
            data.get("amount", tx.amount),
            data.get("fee_amount", tx.fee_amount),
            data.get("source", tx.source),
            data.get("category", tx.category),
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    for key, value in data.items():
        setattr(tx, key, value)
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return _to_read(tx)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    tx = _get_or_404(session, transaction_id)
    session.delete(tx)
    session.commit()
