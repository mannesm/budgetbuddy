# ## Write a test for the transaction API endpoint
#
# from fastapi.testclient import TestClient
#
# from src.budgetbuddy.api.routers import transaction
# from src.budgetbuddy.api.app import app
# from src.budgetbuddy.services.transaction_service import Transaction
#
# from tests.budgetbuddy.db.test_db import TestSessionLocal
#

from uuid import UUID

import pytest


@pytest.mark.smoke
def test_root_ok(client_no_db):
    resp = client_no_db.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.integration
def test_create_transaction(client):
    payload = {"amount": 12.5, "currency": "USD", "description": "lunch"}
    resp = client.post("/transactions/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    # Validate shape
    assert UUID(data["itemid"])  # valid UUID string
    assert data["amount"] == 12.5
    assert data["currency"] == "USD"
    assert data["description"] == "lunch"
    assert "createdtimestamp" in data and "updatedtimestamp" in data


@pytest.mark.integration
def test_transaction_crud_flow(client):
    # Create
    payload = {"amount": 5.0, "currency": "EUR", "description": "coffee"}
    r = client.post("/transactions/", json=payload)
    assert r.status_code == 201
    created = r.json()
    itemid = created["itemid"]

    # Get
    r = client.get(f"/transactions/{itemid}")
    assert r.status_code == 200
    got = r.json()
    assert got["amount"] == 5.0

    # List
    r = client.get("/transactions/?offset=0&limit=10")
    assert r.status_code == 200
    lst = r.json()
    assert any(x["itemid"] == itemid for x in lst)

    # Update
    r = client.patch(f"/transactions/{itemid}", json={"description": "espresso"})
    assert r.status_code == 200
    upd = r.json()
    assert upd["description"] == "espresso"

    # Delete
    r = client.delete(f"/transactions/{itemid}")
    assert r.status_code == 204

    # Ensure 404 after delete
    r = client.get(f"/transactions/{itemid}")
    assert r.status_code == 404
