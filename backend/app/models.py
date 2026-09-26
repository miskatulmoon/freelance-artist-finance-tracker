from datetime import UTC, datetime
from datetime import date as DateType
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

# Money is stored as integer cents. Convert at the API boundary only.
CENTS_PER_DOLLAR = 100


def dollars_to_cents(dollars: float | Decimal) -> int:
    """Convert a dollar amount to integer cents, rounding half-up."""
    return int((Decimal(str(dollars)) * CENTS_PER_DOLLAR).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def cents_to_dollars(cents: int) -> float:
    """Convert integer cents back to dollars for API responses."""
    return cents / CENTS_PER_DOLLAR


class Source(StrEnum):
    COMMISSION = "commission"
    ETSY = "etsy"
    PATREON = "patreon"
    OTHER_INCOME = "other_income"


class Category(StrEnum):
    SUPPLIES = "supplies"
    PLATFORM_FEES = "platform_fees"
    SUBSCRIPTIONS = "subscriptions"
    EQUIPMENT = "equipment"
    OTHER_EXPENSE = "other_expense"


class CommissionStatus(StrEnum):
    AGREED = "agreed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Transaction(SQLModel, table=True):
    __table_args__ = (Index("ix_transaction_type_date", "type", "date"),)

    id: int | None = Field(default=None, primary_key=True)
    type: str = Field(index=True)
    amount_cents: int
    description: str
    date: DateType = Field(index=True)
    fee_amount_cents: int | None = None
    source: str | None = Field(default=None, index=True)
    category: str | None = None
    merchant: str | None = Field(default=None, index=True)
    auto_categorized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    commissions: list["Commission"] = Relationship(back_populates="transaction")


class Commission(SQLModel, table=True):
    __table_args__ = (Index("ix_commission_status_expected_date", "status", "expected_date"),)

    id: int | None = Field(default=None, primary_key=True)
    client: str
    piece: str
    hours_spent: float = 0.0
    amount_cents: int | None = None
    expected_date: DateType | None = Field(default=None, index=True)
    status: str = Field(default=CommissionStatus.IN_PROGRESS.value, index=True)
    transaction_id: int | None = Field(default=None, foreign_key="transaction.id", unique=True)
    income_autologged: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    transaction: Transaction | None = Relationship(back_populates="commissions")
