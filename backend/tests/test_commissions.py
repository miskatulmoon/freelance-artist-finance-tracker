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
