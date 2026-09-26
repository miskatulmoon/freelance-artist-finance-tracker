from tests.conftest import make_tx


def test_commission_effective_rate(client, session):
    income = make_tx("income", 500.0, "portrait comm", source="commission")
    session.add(income)
    session.commit()
    income_id = client.get("/transactions").json()["items"][0]["id"]

    r = client.post(
        "/commissions",
        json={"client": "slime", "piece": "portrait", "hours_spent": 20, "amount": 500, "transaction_id": income_id},
    )
    assert r.status_code == 201
    assert r.json()["effective_rate"] == 25.0


def test_commission_without_hours_has_no_rate(client):
    r = client.post("/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 0})
    assert r.status_code == 201
    assert r.json()["effective_rate"] is None


def test_commission_unlinked_transaction_has_no_rate(client):
    r = client.post("/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 5})
    assert r.json()["effective_rate"] is None


def test_commission_rejects_missing_transaction_link(client):
    response = client.post(
        "/commissions",
        json={"client": "mira", "piece": "sketch", "transaction_id": 999},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "transaction_id must reference an income transaction"


def test_commission_rejects_expense_transaction_link(client, session):
    from tests.conftest import make_tx

    expense = make_tx("expense", 25.0, "paper", category="supplies")
    session.add(expense)
    session.commit()

    response = client.post(
        "/commissions",
        json={"client": "mira", "piece": "sketch", "transaction_id": expense.id},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "transaction_id must reference an income transaction"


def test_commission_rejects_duplicate_transaction_link(client, session):
    from tests.conftest import make_tx

    income = make_tx("income", 250.0, "portrait", source="commission")
    session.add(income)
    session.commit()

    first = client.post(
        "/commissions",
        json={"client": "mira", "piece": "portrait", "transaction_id": income.id},
    )
    second = client.post(
        "/commissions",
        json={"client": "sol", "piece": "icons", "transaction_id": income.id},
    )

    assert first.status_code == 201
    assert second.status_code == 422
    assert second.json()["detail"] == "transaction_id is already linked to a commission"


def test_commission_update_rejects_transaction_link_change(client, session):
    from tests.conftest import make_tx

    first_income = make_tx("income", 250.0, "portrait", source="commission")
    second_income = make_tx("income", 300.0, "icons", source="commission")
    session.add_all([first_income, second_income])
    session.commit()

    first = client.post(
        "/commissions",
        json={"client": "mira", "piece": "portrait", "transaction_id": first_income.id},
    ).json()
    second = client.post(
        "/commissions",
        json={"client": "sol", "piece": "icons", "transaction_id": second_income.id},
    ).json()

    response = client.patch(f"/commissions/{second['id']}", json={"transaction_id": first["transaction_id"]})

    assert response.status_code == 422


def test_patch_commission_status(client):
    created = client.post(
        "/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 5, "amount": 150}
    ).json()
    r = client.patch(f"/commissions/{created['id']}", json={"status": "completed"})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


def test_patch_commission_rejects_term_changes(client):
    created = client.post(
        "/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 5, "amount": 200}
    ).json()

    for field in ("hours_spent", "amount", "expected_date", "client", "piece"):
        response = client.patch(f"/commissions/{created['id']}", json={field: 1 if field != "client" else "x"})
        assert response.status_code == 422, field
        assert created[field] == client.get("/commissions").json()["items"][0][field]


def test_completing_commission_logs_income_automatically(client, session):
    created = client.post(
        "/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 10, "amount": 400}
    ).json()

    r = client.patch(f"/commissions/{created['id']}", json={"status": "completed"})
    assert r.status_code == 200
    body = r.json()
    assert body["income_autologged"] is True
    assert body["transaction_id"] is not None
    assert body["effective_rate"] == 40.0

    slips = client.get("/transactions").json()["items"]
    assert len(slips) == 1
    assert slips[0]["source"] == "commission"
    assert slips[0]["amount"] == 400
    assert f"for {created['client']}" in slips[0]["description"]

    from app.services.stats import balance

    assert balance(session) == 400.0


def test_completing_commission_without_price_fails(client):
    created = client.post("/commissions", json={"client": "mira", "piece": "sketch"}).json()
    r = client.patch(f"/commissions/{created['id']}", json={"status": "completed"})
    assert r.status_code == 422
    assert "agreed price" in r.json()["detail"]
    assert client.get("/commissions").json()["items"][0]["status"] == "in_progress"


def test_completing_commission_with_manual_link_does_not_duplicate_income(client, session):
    from tests.conftest import make_tx

    income = make_tx("income", 300.0, "portrait", source="commission")
    session.add(income)
    session.commit()

    created = client.post(
        "/commissions",
        json={"client": "mira", "piece": "portrait", "hours_spent": 10, "amount": 300, "transaction_id": income.id},
    ).json()
    r = client.patch(f"/commissions/{created['id']}", json={"status": "completed"})

    assert r.status_code == 200
    assert r.json()["income_autologged"] is False
    assert len(client.get("/transactions").json()["items"]) == 1


def test_recompleting_commission_does_not_duplicate_income(client):
    created = client.post(
        "/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 2, "amount": 100}
    ).json()
    client.patch(f"/commissions/{created['id']}", json={"status": "completed"})
    client.patch(f"/commissions/{created['id']}", json={"status": "completed"})

    assert len(client.get("/transactions").json()["items"]) == 1


def test_reopening_commission_retracts_autologged_income(client, session):
    created = client.post(
        "/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 2, "amount": 100}
    ).json()
    client.patch(f"/commissions/{created['id']}", json={"status": "completed"})

    r = client.patch(f"/commissions/{created['id']}", json={"status": "in_progress"})

    assert r.status_code == 200
    assert r.json()["transaction_id"] is None
    assert r.json()["income_autologged"] is False
    assert client.get("/transactions").json()["items"] == []

    from app.services.stats import balance

    assert balance(session) == 0.0


def test_reopening_commission_keeps_manually_linked_income(client, session):
    from tests.conftest import make_tx

    income = make_tx("income", 300.0, "portrait", source="commission")
    session.add(income)
    session.commit()

    created = client.post(
        "/commissions",
        json={"client": "mira", "piece": "portrait", "transaction_id": income.id},
    ).json()
    client.patch(f"/commissions/{created['id']}", json={"status": "completed"})
    r = client.patch(f"/commissions/{created['id']}", json={"status": "in_progress"})

    assert r.status_code == 200
    assert r.json()["transaction_id"] == income.id
    assert len(client.get("/transactions").json()["items"]) == 1


def test_cancelling_completed_commission_retracts_income(client):
    created = client.post(
        "/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 2, "amount": 100}
    ).json()
    client.patch(f"/commissions/{created['id']}", json={"status": "completed"})
    client.patch(f"/commissions/{created['id']}", json={"status": "cancelled"})

    assert client.get("/transactions").json()["items"] == []


def test_deleting_completed_commission_retracts_income(client):
    created = client.post(
        "/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 2, "amount": 100}
    ).json()
    client.patch(f"/commissions/{created['id']}", json={"status": "completed"})

    assert client.delete(f"/commissions/{created['id']}").status_code == 204
    assert client.get("/transactions").json()["items"] == []


def test_creating_completed_commission_logs_income_automatically(client):
    r = client.post(
        "/commissions",
        json={"client": "mira", "piece": "sketch", "hours_spent": 4, "amount": 200, "status": "completed"},
    )
    assert r.status_code == 201
    assert r.json()["income_autologged"] is True
    assert r.json()["effective_rate"] == 50.0
    assert len(client.get("/transactions").json()["items"]) == 1


def test_commissions_summary_by_status(client):
    client.post("/commissions", json={"client": "a", "piece": "agreed piece", "amount": 100, "status": "agreed"})
    client.post("/commissions", json={"client": "b", "piece": "active piece", "amount": 50, "status": "in_progress"})
    client.post("/commissions", json={"client": "c", "piece": "done piece", "amount": 300, "status": "completed"})
    client.post("/commissions", json={"client": "d", "piece": "dropped piece", "amount": 80, "status": "cancelled"})

    r = client.get("/commissions/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["expected_income"] == 150.0
    assert body["earned_income"] == 300.0
    assert body["lost_income"] == 80.0
    assert body["counts"] == {"agreed": 1, "in_progress": 1, "completed": 1, "cancelled": 1}
    assert body["active_count"] == 2


def test_delete_commission(client):
    created = client.post("/commissions", json={"client": "mira", "piece": "sketch"}).json()
    assert client.delete(f"/commissions/{created['id']}").status_code == 204
    assert client.delete(f"/commissions/{created['id']}").status_code == 404


def test_commission_rejects_empty_client(client):
    r = client.post("/commissions", json={"client": "", "piece": "x"})
    assert r.status_code == 422


def test_list_commissions_returns_envelope_with_total(client):
    client.post("/commissions", json={"client": "a", "piece": "one"})
    client.post("/commissions", json={"client": "b", "piece": "two"})

    body = client.get("/commissions").json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 50
    assert body["offset"] == 0


def test_list_commissions_paginates(client):
    for i in range(5):
        client.post("/commissions", json={"client": f"c{i}", "piece": f"piece-{i}"})

    first = client.get("/commissions", params={"limit": 2}).json()
    second = client.get("/commissions", params={"limit": 2, "offset": 2}).json()
    assert first["total"] == 5
    assert len(first["items"]) == 2
    assert second["total"] == 5
    assert len(second["items"]) == 2
    first_ids = {row["id"] for row in first["items"]}
    second_ids = {row["id"] for row in second["items"]}
    assert first_ids.isdisjoint(second_ids)


def test_list_commissions_filters_by_status(client):
    client.post("/commissions", json={"client": "a", "piece": "x", "status": "agreed"})
    client.post("/commissions", json={"client": "b", "piece": "y", "status": "completed", "amount": 50})
    client.post("/commissions", json={"client": "c", "piece": "z", "status": "in_progress"})

    body = client.get("/commissions", params={"status": "completed"}).json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "completed"


def test_list_commissions_rejects_invalid_status(client):
    assert client.get("/commissions", params={"status": "bogus"}).status_code == 422


def test_list_commissions_rejects_invalid_pagination_bounds(client):
    assert client.get("/commissions", params={"limit": 0}).status_code == 422
    assert client.get("/commissions", params={"limit": 101}).status_code == 422
    assert client.get("/commissions", params={"offset": -1}).status_code == 422


def test_list_commissions_orders_active_first(client):
    client.post("/commissions", json={"client": "done", "piece": "x", "status": "completed", "amount": 10})
    client.post("/commissions", json={"client": "work", "piece": "y", "status": "in_progress"})
    client.post("/commissions", json={"client": "lost", "piece": "z", "status": "cancelled"})

    items = client.get("/commissions").json()["items"]
    assert [row["status"] for row in items] == ["in_progress", "completed", "cancelled"]
