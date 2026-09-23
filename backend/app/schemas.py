from datetime import date as DateType
from typing import Literal

from sqlmodel import Field, SQLModel

from app.models import Category, CommissionStatus, Source


class TransactionCreate(SQLModel):
    type: Literal["income", "expense"]
    amount: float = Field(gt=0)
    description: str = Field(min_length=1)
    date: DateType = Field(default_factory=DateType.today)
    fee_amount: float | None = Field(default=None, ge=0)
    source: Source | None = None
    category: Category | None = None
    merchant: str | None = None


class TransactionUpdate(SQLModel):
    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1)
    date: DateType | None = None
    fee_amount: float | None = Field(default=None, ge=0)
    source: Source | None = None
    category: Category | None = None
    merchant: str | None = None


class TransactionRead(SQLModel):
    id: int
    type: str
    amount: float
    net_amount: float
    description: str
    date: DateType
    fee_amount: float | None
    source: str | None
    category: str | None
    merchant: str | None
    auto_categorized: bool


class CommissionCreate(SQLModel):
    client: str = Field(min_length=1)
    piece: str = Field(min_length=1)
    hours_spent: float = Field(default=0, ge=0)
    amount: float | None = Field(default=None, gt=0)
    expected_date: DateType | None = None
    status: CommissionStatus = CommissionStatus.IN_PROGRESS
    transaction_id: int | None = None


class CommissionUpdate(SQLModel):
    client: str | None = Field(default=None, min_length=1)
    piece: str | None = Field(default=None, min_length=1)
    hours_spent: float | None = Field(default=None, ge=0)
    amount: float | None = Field(default=None, gt=0)
    expected_date: DateType | None = None
    status: CommissionStatus | None = None
    transaction_id: int | None = None


class CommissionRead(SQLModel):
    id: int
    client: str
    piece: str
    hours_spent: float
    amount: float | None
    expected_date: DateType | None
    status: str
    transaction_id: int | None
    effective_rate: float | None


class ChatRequest(SQLModel):
    question: str = Field(min_length=1)
