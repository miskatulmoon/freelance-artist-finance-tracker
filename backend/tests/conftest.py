from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from app.services.llm import get_llm


class FakeLLM:
    """Deterministic stand-in for the real provider."""

    def categorize(self, type: str, description: str, merchant: str, amount: float) -> dict:
        if type == "income":
            return {"source": "etsy", "confidence": 0.9}
        return {"category": "supplies", "confidence": 0.9}

    def narrate_insights(self, metrics: dict) -> str:
        return f"FAKE_INSIGHTS balance={metrics['balance']} rate={metrics['hourly_rate']}"

    def narrate_cashflow(self, radar: dict) -> str:
        return f"FAKE_CASHFLOW level={radar['level']} coverage={radar['coverage_pct']}"

    def answer_question(self, question: str, bundle: dict) -> str:
        return f"FAKE_ANSWER q={question} balance={bundle['balance']}"


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(engine):
    def override_get_session():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_tx(
    type: str,
    amount: float,
    description: str,
    tx_date: date | None = None,
    fee: float | None = None,
    source: str | None = None,
    category: str | None = None,
    merchant: str | None = None,
):
    from app.models import Transaction

    return Transaction(
        type=type,
        amount=amount,
        description=description,
        date=tx_date or (date.today() - timedelta(days=1)),
        fee_amount=fee,
        source=source,
        category=category,
        merchant=merchant,
    )


def make_commission(
    client_name: str = "mira",
    piece: str = "portrait",
    hours: float = 10.0,
    amount: float | None = 300.0,
    expected_date: date | None = None,
    status: str = "agreed",
    transaction_id: int | None = None,
):
    from app.models import Commission

    return Commission(
        client=client_name,
        piece=piece,
        hours_spent=hours,
        amount=amount,
        expected_date=expected_date,
        status=status,
        transaction_id=transaction_id,
    )


@pytest.fixture
def legacy_engine():
    """An engine whose commission table predates the income_autologged column."""
    legacy = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with legacy.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE commission ("
                "id INTEGER PRIMARY KEY, client VARCHAR NOT NULL, piece VARCHAR NOT NULL, "
                "hours_spent FLOAT NOT NULL, amount FLOAT, expected_date DATE, status VARCHAR NOT NULL, "
                "transaction_id INTEGER, created_at TIMESTAMP)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO commission (id, client, piece, hours_spent, amount, status, created_at) "
                "VALUES (1, 'old client', 'old piece', 5.0, 200.0, 'completed', '2026-01-01 00:00:00')"
            )
        )
    yield legacy
    legacy.dispose()
