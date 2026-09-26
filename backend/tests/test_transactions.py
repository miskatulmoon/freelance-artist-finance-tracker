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
    assert body["net_amount"] is None


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


def test_create_rejects_fee_larger_than_income(client):
    r = client.post(
        "/transactions",
        json={"type": "income", "amount": 10, "fee_amount": 10.01, "description": "x"},
    )
    assert r.status_code == 422


def test_create_rejects_fields_for_wrong_transaction_type(client):
    income = client.post(
        "/transactions",
        json={"type": "income", "amount": 10, "category": "supplies", "description": "x"},
    )
    expense = client.post(
        "/transactions",
        json={"type": "expense", "amount": 10, "source": "etsy", "description": "x"},
    )
    assert income.status_code == 422
    assert expense.status_code == 422


def test_patch_rejects_invalid_merged_state(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("income", 10.0, "sale", source="etsy"))
    session.commit()
    row_id = client.get("/transactions").json()["items"][0]["id"]

    response = client.patch(f"/transactions/{row_id}", json={"fee_amount": 10.01})

    assert response.status_code == 422
    assert client.get("/transactions").json()["items"][0]["fee_amount"] is None


def test_list_and_filter_by_source(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("income", 100.0, "comm", source="commission"))
    session.add(make_tx("income", 50.0, "sale", source="etsy", fee=2.0))
    session.commit()

    body = client.get("/transactions").json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 50
    assert body["offset"] == 0

    only_etsy = client.get("/transactions", params={"source": "etsy"}).json()
    assert only_etsy["total"] == 1
    assert len(only_etsy["items"]) == 1
    assert only_etsy["items"][0]["source"] == "etsy"


def test_list_paginates_in_stable_sort_order(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "old", tx_date=date(2026, 8, 1)))
    session.add(make_tx("expense", 20.0, "new", tx_date=date(2026, 9, 1)))
    session.add(make_tx("expense", 30.0, "newest", tx_date=date(2026, 9, 1)))
    session.commit()

    first_page = client.get("/transactions", params={"limit": 2}).json()
    second_page = client.get("/transactions", params={"limit": 2, "offset": 2}).json()

    assert first_page["total"] == 3
    assert [row["description"] for row in first_page["items"]] == ["newest", "new"]
    assert second_page["total"] == 3
    assert [row["description"] for row in second_page["items"]] == ["old"]


def test_list_rejects_invalid_pagination_bounds(client):
    assert client.get("/transactions", params={"limit": 0}).status_code == 422
    assert client.get("/transactions", params={"limit": 101}).status_code == 422
    assert client.get("/transactions", params={"offset": -1}).status_code == 422


def test_filter_by_date_range(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "old", tx_date=date(2026, 8, 1)))
    session.add(make_tx("expense", 20.0, "new", tx_date=date(2026, 9, 1)))
    session.commit()

    body = client.get("/transactions", params={"from_date": "2026-09-01"}).json()
    assert body["total"] == 1
    assert body["items"][0]["description"] == "new"


def test_patch_transaction(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "supplies"))
    session.commit()
    row_id = client.get("/transactions").json()["items"][0]["id"]

    r = client.patch(f"/transactions/{row_id}", json={"amount": 12.0, "merchant": "Blick"})
    assert r.status_code == 200
    assert r.json()["amount"] == 12.0
    assert r.json()["merchant"] == "Blick"


def test_delete_transaction(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "supplies"))
    session.commit()
    row_id = client.get("/transactions").json()["items"][0]["id"]

    assert client.delete(f"/transactions/{row_id}").status_code == 204
    assert client.get("/transactions").json()["items"] == []
    assert client.get("/transactions").json()["total"] == 0
    assert client.delete(f"/transactions/{row_id}").status_code == 404


def test_list_rejects_invalid_enum_filters(client):
    assert client.get("/transactions", params={"source": "bogus"}).status_code == 422
    assert client.get("/transactions", params={"category": "bogus"}).status_code == 422
    assert client.get("/transactions", params={"type": "bogus"}).status_code == 422


def test_list_rejects_invalid_sort(client):
    assert client.get("/transactions", params={"sort": "DROP TABLE transaction"}).status_code == 422


def test_list_sorts_by_amount(client, session):
    from tests.conftest import make_tx

    session.add(make_tx("expense", 10.0, "cheap"))
    session.add(make_tx("expense", 30.0, "pricey"))
    session.add(make_tx("expense", 20.0, "mid"))
    session.commit()

    body = client.get("/transactions", params={"sort": "amount_desc"}).json()
    assert [row["description"] for row in body["items"]] == ["pricey", "mid", "cheap"]

    body = client.get("/transactions", params={"sort": "amount_asc"}).json()
    assert [row["description"] for row in body["items"]] == ["cheap", "mid", "pricey"]


def test_list_total_ignores_pagination_window(client, session):
    from tests.conftest import make_tx

    for i in range(5):
        session.add(make_tx("expense", 10.0 + i, f"item-{i}"))
    session.commit()

    body = client.get("/transactions", params={"limit": 2, "offset": 2}).json()
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 2
