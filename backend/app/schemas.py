from datetime import date as DateType
from typing import Literal

from pydantic import ConfigDict, model_validator
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

    @model_validator(mode="after")
    def validate_financial_fields(self) -> "TransactionCreate":
        validate_transaction_fields(
            self.type,
            self.amount,
            self.fee_amount,
            self.source,
            self.category,
        )
        return self


class TransactionUpdate(SQLModel):
    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1)
    date: DateType | None = None
    fee_amount: float | None = Field(default=None, ge=0)
    source: Source | None = None
    category: Category | None = None
    merchant: str | None = None


def validate_transaction_fields(
    type: str,
    amount: float,
    fee_amount: float | None,
    source: Source | str | None,
    category: Category | str | None,
) -> None:
    if type == "income" and category is not None:
        raise ValueError("income transactions cannot have an expense category")
    if type == "expense" and source is not None:
        raise ValueError("expense transactions cannot have an income source")
    if type == "expense" and fee_amount is not None:
        raise ValueError("expense transactions cannot have a fee")
    if fee_amount is not None and fee_amount > amount:
        raise ValueError("fee_amount cannot exceed amount")


class TransactionRead(SQLModel):
    id: int
    type: str
    amount: float
    net_amount: float | None
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
    """Terms (price, hours, expected date) lock when the commission is logged.

    Only progress — the status — can be updated afterwards.
    """

    model_config = ConfigDict(extra="forbid")

    status: CommissionStatus


class CommissionRead(SQLModel):
    id: int
    client: str
    piece: str
    hours_spent: float
    amount: float | None
    expected_date: DateType | None
    status: str
    transaction_id: int | None
    income_autologged: bool
    effective_rate: float | None


class CommissionSummary(SQLModel):
    expected_income: float
    earned_income: float
    lost_income: float
    counts: dict[str, int]
    active_count: int


class ChatRequest(SQLModel):
    question: str = Field(min_length=1)
