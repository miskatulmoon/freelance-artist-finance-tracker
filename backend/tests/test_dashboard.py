import json

from tests.conftest import make_tx


def test_dashboard_summary_shape(client, session):
    session.add(make_tx("income", 500.0, "commission", source="commission"))
    session.add(make_tx("income", 100.0, "etsy", source="etsy", fee=4.0))
    session.add(make_tx("expense", 30.0, "paints", category="supplies"))
    session.commit()

    body = client.get("/dashboard/summary").json()
    assert body["balance"] == 566.0
    assert body["per_source_net"] == {"commission": 500.0, "etsy": 96.0}
    assert body["total_fees"] == 4.0
    assert len(body["monthly_trend"]) == 6
    assert body["monthly_trend"][0]["month"] <= body["monthly_trend"][-1]["month"]


def test_cashflow_radar_endpoint(client, session):
    body = client.get("/cashflow/radar").json()
    assert set(body) == {
        "balance",
        "burn_per_day",
        "burn_next_30d",
        "committed_next_30d",
        "projected_balance_30d",
        "coverage_pct",
        "level",
        "as_of",
        "projection",
        "runway_days",
        "projected_zero_date",
    }
    assert body["level"] in {"healthy", "moderate", "low", "unknown"}


def test_dashboard_insights_uses_llm(client, session):
    session.add(make_tx("income", 500.0, "commission", source="commission"))
    session.commit()
    body = client.post("/dashboard/insights").json()
    assert "FAKE_INSIGHTS" in body["insights"]


def test_cashflow_insights_includes_narrative(client, session):
    body = client.post("/cashflow/radar/insights").json()
    assert "FAKE_CASHFLOW" in body["narrative"]
    assert "radar" in body


def test_chat_uses_llm(client, session):
    session.add(make_tx("income", 500.0, "commission", source="commission"))
    session.commit()
    r = client.post("/chat", json={"question": "how is my balance?"})
    assert r.status_code == 200
    assert "FAKE_ANSWER" in r.json()["answer"]


def test_chat_rejects_empty_question(client):
    assert client.post("/chat", json={"question": ""}).status_code == 422


def test_chat_stream_returns_sse_deltas(client, session):
    session.add(make_tx("income", 500.0, "commission", source="commission"))
    session.commit()
    with client.stream("POST", "/chat/stream", json={"question": "how is my balance?"}) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        body = "".join(chunk.decode() for chunk in r.iter_raw())
    assert body.endswith("data: [DONE]\n\n")
    deltas = [
        json.loads(line[6:])["delta"]
        for line in body.split("\n\n")
        if line.startswith("data: ") and line != "data: [DONE]"
    ]
    assert "".join(deltas) == "FAKE_ANSWER q=how is my balance? balance=500.0"
    assert len(deltas) > 1


def test_chat_stream_degrades_to_fallback(client, session, monkeypatch):
    from app.main import app
    from app.services.llm import FallbackClient, HeuristicFallback, OpenAIClient, get_llm

    def broken_stream(self, question: str, bundle: dict):
        raise RuntimeError("provider down")
        yield

    monkeypatch.setattr(OpenAIClient, "stream_answer_question", broken_stream)
    # Bypass the FakeLLM override: wrap a real OpenAIClient (whose stream is now
    # broken) in FallbackClient so the endpoint must degrade to heuristics.
    primary = OpenAIClient.__new__(OpenAIClient)
    app.dependency_overrides[get_llm] = lambda: FallbackClient(primary)
    session.add(make_tx("income", 500.0, "commission", source="commission"))
    session.commit()
    with client.stream("POST", "/chat/stream", json={"question": "what is my balance?"}) as r:
        assert r.status_code == 200
        body = "".join(chunk.decode() for chunk in r.iter_raw())
    deltas = [
        json.loads(line[6:])["delta"]
        for line in body.split("\n\n")
        if line.startswith("data: ") and line != "data: [DONE]"
    ]
    assert "".join(deltas) == HeuristicFallback().answer_question("what is my balance?", {"balance": 500.0})


def test_chat_stream_rejects_empty_question(client):
    assert client.post("/chat/stream", json={"question": ""}).status_code == 422
