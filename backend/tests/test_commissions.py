from tests.conftest import make_tx


def test_commission_effective_rate(client, session):
    income = make_tx("income", 500.0, "portrait comm", source="commission")
    session.add(income)
    session.commit()
    income_id = client.get("/transactions").json()[0]["id"]

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


def test_commission_update_rejects_duplicate_transaction_link(client, session):
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
    assert response.json()["detail"] == "transaction_id is already linked to a commission"


def test_patch_commission_status(client):
    created = client.post("/commissions", json={"client": "mira", "piece": "sketch", "hours_spent": 5}).json()
    r = client.patch(f"/commissions/{created['id']}", json={"status": "completed", "hours_spent": 8})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    assert r.json()["hours_spent"] == 8.0


def test_delete_commission(client):
    created = client.post("/commissions", json={"client": "mira", "piece": "sketch"}).json()
    assert client.delete(f"/commissions/{created['id']}").status_code == 204
    assert client.delete(f"/commissions/{created['id']}").status_code == 404


def test_commission_rejects_empty_client(client):
    r = client.post("/commissions", json={"client": "", "piece": "x"})
    assert r.status_code == 422
