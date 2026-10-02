import csv
from datetime import date as DateType
from io import StringIO
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models import Category, Source, Transaction, cents_to_dollars, dollars_to_cents
from app.schemas import (
    TransactionCreate,
    TransactionImportError,
    TransactionImportRow,
    TransactionImportSummary,
    TransactionPage,
    TransactionRead,
    TransactionUpdate,
    validate_transaction_fields,
)
from app.services.llm import LLMClient, get_llm

router = APIRouter(prefix="/transactions", tags=["transactions"])

TransactionSort = Literal["date_desc", "date_asc", "amount_desc", "amount_asc"]


def _categorize(tx: Transaction, llm: LLMClient) -> None:
    result = llm.categorize(
        type=tx.type,
        description=tx.description,
        merchant=tx.merchant or "",
        amount=cents_to_dollars(tx.amount_cents),
    )
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


@router.get("", response_model=TransactionPage)
def list_transactions(
    source: Source | None = None,
    category: Category | None = None,
    type: Literal["income", "expense"] | None = None,
    from_date: DateType | None = None,
    to_date: DateType | None = None,
    sort: TransactionSort = Query(default="date_desc"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    filters = []
    if source is not None:
        filters.append(Transaction.source == source.value)
    if category is not None:
        filters.append(Transaction.category == category.value)
    if type is not None:
        filters.append(Transaction.type == type)
    if from_date is not None:
        filters.append(Transaction.date >= from_date)
    if to_date is not None:
        filters.append(Transaction.date <= to_date)

    count_stmt = select(func.count()).select_from(Transaction)
    for criterion in filters:
        count_stmt = count_stmt.where(criterion)
    total = int(session.exec(count_stmt).one() or 0)

    ordering = {
        "date_desc": (Transaction.date.desc(), Transaction.id.desc()),
        "date_asc": (Transaction.date.asc(), Transaction.id.asc()),
        "amount_desc": (Transaction.amount_cents.desc(), Transaction.id.desc()),
        "amount_asc": (Transaction.amount_cents.asc(), Transaction.id.asc()),
    }[sort]

    query = select(Transaction)
    for criterion in filters:
        query = query.where(criterion)
    rows = session.exec(query.order_by(*ordering).offset(offset).limit(limit)).all()
    return TransactionPage(
        items=[TransactionRead.from_model(tx) for tx in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(
    payload: TransactionCreate, session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)
):
    tx = Transaction(
        type=payload.type,
        amount_cents=payload.amount_cents,
        description=payload.description,
        date=payload.date,
        fee_amount_cents=payload.fee_amount_cents,
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
    return TransactionRead.from_model(tx)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, payload: TransactionUpdate, session: Session = Depends(get_session)):
    tx = _get_or_404(session, transaction_id)
    data = payload.model_dump_cents()
    if "source" in data:
        data["source"] = data["source"].value if data["source"] else None
    if "category" in data:
        data["category"] = data["category"].value if data["category"] else None
    try:
        validate_transaction_fields(
            tx.type,
            cents_to_dollars(data.get("amount_cents", tx.amount_cents)),
            (cents_to_dollars(fee) if (fee := data.get("fee_amount_cents", tx.fee_amount_cents)) is not None else None),
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
    return TransactionRead.from_model(tx)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    tx = _get_or_404(session, transaction_id)
    session.delete(tx)
    session.commit()


@router.get("/export")
def export_transactions(
    source: Source | None = None,
    category: Category | None = None,
    type: Literal["income", "expense"] | None = None,
    from_date: DateType | None = None,
    to_date: DateType | None = None,
    sort: TransactionSort = Query(default="date_desc"),
    session: Session = Depends(get_session),
):
    filters = []
    if source is not None:
        filters.append(Transaction.source == source.value)
    if category is not None:
        filters.append(Transaction.category == category.value)
    if type is not None:
        filters.append(Transaction.type == type)
    if from_date is not None:
        filters.append(Transaction.date >= from_date)
    if to_date is not None:
        filters.append(Transaction.date <= to_date)

    ordering = {
        "date_desc": (Transaction.date.desc(), Transaction.id.desc()),
        "date_asc": (Transaction.date.asc(), Transaction.id.asc()),
        "amount_desc": (Transaction.amount_cents.desc(), Transaction.id.desc()),
        "amount_asc": (Transaction.amount_cents.asc(), Transaction.id.asc()),
    }[sort]

    query = select(Transaction).where(*filters).order_by(*ordering)
    rows = session.exec(query).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "type",
            "amount",
            "net_amount",
            "description",
            "date",
            "fee_amount",
            "source",
            "category",
            "merchant",
            "auto_categorized",
        ]
    )
    for tx in rows:
        net = tx.amount_cents - (tx.fee_amount_cents or 0)
        net_amount = cents_to_dollars(net) if tx.type == "income" else ""
        fee = cents_to_dollars(tx.fee_amount_cents) if tx.fee_amount_cents is not None else ""
        writer.writerow(
            [
                tx.id,
                tx.type,
                f"{cents_to_dollars(tx.amount_cents):.2f}",
                f"{net_amount:.2f}" if tx.type == "income" else "",
                tx.description,
                tx.date.isoformat(),
                f"{fee:.2f}" if fee != "" else "",
                tx.source or "",
                tx.category or "",
                tx.merchant or "",
                tx.auto_categorized,
            ]
        )

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="transactions.csv"'},
    )


MAX_IMPORT_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMPORT_ROWS = 5000


@router.post("/import", response_model=TransactionImportSummary)
async def import_transactions(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    llm: LLMClient = Depends(get_llm),
):
    content = await file.read()
    if len(content) > MAX_IMPORT_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(StringIO(text))
    rows = list(reader)
    if len(rows) > MAX_IMPORT_ROWS:
        raise HTTPException(status_code=413, detail="Too many rows")

    created = 0
    skipped = 0
    errors: list[TransactionImportError] = []

    for idx, raw in enumerate(rows, start=2):  # header is row 1
        # Build normalized dict
        normalized = {}
        for k, v in raw.items():
            normalized[k.strip().lower()] = v.strip() if isinstance(v, str) else v
        try:
            # Validate and coerce via schema
            row = TransactionImportRow(
                type=normalized.get("type", ""),
                amount=float(normalized.get("amount", 0)),
                description=normalized.get("description", ""),
                date=DateType.fromisoformat(normalized.get("date", "")),
                fee_amount=float(normalized.get("fee_amount")) if normalized.get("fee_amount") else None,
                source=normalized.get("source") if normalized.get("source") else None,
                category=normalized.get("category") if normalized.get("category") else None,
                merchant=normalized.get("merchant") or None,
            )
            # Validate business rules
            validate_transaction_fields(row.type, row.amount, row.fee_amount, row.source, row.category)

            tx = Transaction(
                type=row.type,
                amount_cents=dollars_to_cents(row.amount),
                description=row.description,
                date=row.date,
                fee_amount_cents=dollars_to_cents(row.fee_amount) if row.fee_amount is not None else None,
                merchant=row.merchant,
            )
            if row.type == "income":
                tx.source = row.source
            else:
                tx.category = row.category

            needs_categorization = (row.type == "income" and tx.source is None) or (
                row.type == "expense" and tx.category is None
            )
            if needs_categorization:
                _categorize(tx, llm)

            # Final validation after categorization
            validate_transaction_fields(
                tx.type,
                cents_to_dollars(tx.amount_cents),
                cents_to_dollars(tx.fee_amount_cents) if tx.fee_amount_cents else None,
                tx.source,
                tx.category,
            )

            session.add(tx)
            session.commit()
            session.refresh(tx)
            created += 1
        except Exception as e:
            session.rollback()
            errors.append(TransactionImportError(row=idx, message=str(e)))
            skipped += 1

    return TransactionImportSummary(created=created, skipped=skipped, errors=errors)
