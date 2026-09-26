from datetime import date as DateType
from typing import TYPE_CHECKING, Literal

from pydantic import ConfigDict, model_validator
from sqlmodel import Field, SQLModel

from app.models import Category, CommissionStatus, Source, cents_to_dollars, dollars_to_cents

if TYPE_CHECKING:
    from app.models import Commission, Transaction


class TransactionCreate(SQLModel):
    """API boundary: accepts dollars, exposes integer cents to the domain."""

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

    @property
    def amount_cents(self) -> int:
        return dollars_to_cents(self.amount)

    @property
    def fee_amount_cents(self) -> int | None:
        return None if self.fee_amount is None else dollars_to_cents(self.fee_amount)


class TransactionUpdate(SQLModel):
    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1)
    date: DateType | None = None
    fee_amount: float | None = Field(default=None, ge=0)
    source: Source | None = None
    category: Category | None = None
    merchant: str | None = None

    def model_dump_cents(self) -> dict:
        """Dump set fields, converting dollar amounts to integer cents."""
        data = self.model_dump(exclude_unset=True)
        if "amount" in data:
            data["amount_cents"] = dollars_to_cents(data.pop("amount"))
        if "fee_amount" in data:
            fee = data.pop("fee_amount")
            data["fee_amount_cents"] = None if fee is None else dollars_to_cents(fee)
        return data


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
    type: Literal["income", "expense"]
    amount: float
    net_amount: float | None
    description: str
    date: DateType
    fee_amount: float | None
    source: Source | None
    category: Category | None
    merchant: str | None
    auto_categorized: bool

    @classmethod
    def from_model(cls, tx: "Transaction") -> "TransactionRead":
        """API boundary: convert stored integer cents back to dollars."""
        net_cents = tx.amount_cents - (tx.fee_amount_cents or 0)
        return cls(
            id=tx.id,
            type=tx.type,
            amount=cents_to_dollars(tx.amount_cents),
            net_amount=None if tx.type == "expense" else cents_to_dollars(net_cents),
            description=tx.description,
            date=tx.date,
            fee_amount=None if tx.fee_amount_cents is None else cents_to_dollars(tx.fee_amount_cents),
            source=tx.source,
            category=tx.category,
            merchant=tx.merchant,
            auto_categorized=tx.auto_categorized,
        )


class CommissionCreate(SQLModel):
    """API boundary: accepts dollars, exposes integer cents to the domain."""

    client: str = Field(min_length=1)
    piece: str = Field(min_length=1)
    hours_spent: float = Field(default=0, ge=0)
    amount: float | None = Field(default=None, gt=0)
    expected_date: DateType | None = None
    status: CommissionStatus = CommissionStatus.IN_PROGRESS
    transaction_id: int | None = None

    @property
    def amount_cents(self) -> int | None:
        return None if self.amount is None else dollars_to_cents(self.amount)


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

    @classmethod
    def from_model(cls, c: "Commission") -> "CommissionRead":
        """API boundary: convert stored integer cents back to dollars."""
        rate = None
        tx = c.transaction
        if tx and tx.type == "income" and c.hours_spent > 0:
            net_cents = tx.amount_cents - (tx.fee_amount_cents or 0)
            rate = round(cents_to_dollars(net_cents) / c.hours_spent, 2)
        return cls(
            id=c.id,
            client=c.client,
            piece=c.piece,
            hours_spent=c.hours_spent,
            amount=None if c.amount_cents is None else cents_to_dollars(c.amount_cents),
            expected_date=c.expected_date,
            status=c.status,
            transaction_id=c.transaction_id,
            income_autologged=bool(c.income_autologged),
            effective_rate=rate,
        )


class CommissionSummary(SQLModel):
    expected_income: float
    earned_income: float
    lost_income: float
    counts: dict[str, int]
    active_count: int


class TrendPoint(SQLModel):
    month: str
    income: float
    expense: float
    net: float


class MerchantTotal(SQLModel):
    merchant: str
    total: float


class DashboardSummary(SQLModel):
    balance: float
    per_source_net: dict[str, float]
    monthly_trend: list[TrendPoint]
    top_merchants: list[MerchantTotal]
    total_fees: float
    hourly_rate: float | None


class RadarPoint(SQLModel):
    day: int
    date: str
    balance: float


class CashflowRadarRead(SQLModel):
    balance: float
    burn_per_day: float
    burn_next_30d: float
    committed_next_30d: float
    projected_balance_30d: float
    coverage_pct: float | None
    level: Literal["healthy", "moderate", "low", "unknown"]
    as_of: str
    projection: list[RadarPoint]
    runway_days: float | None
    projected_zero_date: str | None


class InsightsResponse(SQLModel):
    insights: str


class ChatResponse(SQLModel):
    answer: str


class CashflowInsightsResponse(SQLModel):
    radar: CashflowRadarRead
    narrative: str


class ChatRequest(SQLModel):
    question: str = Field(min_length=1)
