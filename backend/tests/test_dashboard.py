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
    assert len(body["monthly_trend"]) >= 1
    assert body["monthly_trend"][0]["month"] >= body["monthly_trend"][-1]["month"]


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
