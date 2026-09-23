from datetime import date


def test_create_income_autocategorizes(client):
    r = client.post(
        "/transactions",
        json={"type": "income", "amount": 40.0, "description": "sticker sheet sale", "date": "2026-09-10"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["source"] == "etsy"
    assert body["auto_categorized"] is True
    assert body["net_amount"] == 40.0


def test_create_expense_autocategorizes(client):
    r = client.post("/transactions", json={"type": "expense", "amount": 15.5, "description": "paints"})
    assert r.status_code == 201
    body = r.json()
    assert body["category"] == "supplies"
    assert body["auto_categorized"] is True


def test_create_income_with_explicit_source_skips_autocat(client):
    r = client.post(
        "/transactions",
        json={"type": "income", "amount": 250.0, "description": "commission", "source": "commission"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["source"] == "commission"
    assert body["auto_categorized"] is False


def test_net_amount_subtracts_fee(client):
    r = client.post(
        "/transactions",
        json={"type": "income", "amount": 120.0, "description": "etsy sale", "fee_amount": 4.2, "source": "etsy"},
    )
    assert r.json()["net_amount"] == 115.8


def test_create_rejects_bad_type(client):
    r = client.post("/transactions", json={"type": "bogus", "amount": 10, "description": "x"})
    assert r.status_code == 422


def test_create_rejects_nonpositive_amount(client):
    r = client.post("/transactions", json={"type": "income", "amount": 0, "description": "x"})
    assert r.status_code == 422


def test_list_and_filter_by_source(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("income", 100.0, "comm", source="commission"))
    session.add(make_tx("income", 50.0, "sale", source="etsy", fee=2.0))
    session.commit()

    all_rows = client.get("/transactions").json()
    assert len(all_rows) == 2

    only_etsy = client.get("/transactions", params={"source": "etsy"}).json()
    assert len(only_etsy) == 1
    assert only_etsy[0]["source"] == "etsy"


def test_filter_by_date_range(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "old", tx_date=date(2026, 8, 1)))
    session.add(make_tx("expense", 20.0, "new", tx_date=date(2026, 9, 1)))
    session.commit()

    rows = client.get("/transactions", params={"from_date": "2026-09-01"}).json()
    assert len(rows) == 1
    assert rows[0]["description"] == "new"


def test_patch_transaction(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "supplies"))
    session.commit()
    row_id = client.get("/transactions").json()[0]["id"]

    r = client.patch(f"/transactions/{row_id}", json={"amount": 12.0, "merchant": "Blick"})
    assert r.status_code == 200
    assert r.json()["amount"] == 12.0
    assert r.json()["merchant"] == "Blick"


def test_delete_transaction(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "supplies"))
    session.commit()
    row_id = client.get("/transactions").json()[0]["id"]

    assert client.delete(f"/transactions/{row_id}").status_code == 204
    assert client.get("/transactions").json() == []
    assert client.delete(f"/transactions/{row_id}").status_code == 404
