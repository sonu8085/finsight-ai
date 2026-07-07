"""Tests for transaction CRUD, filtering, pagination, and bulk delete."""
import pytest
from httpx import AsyncClient


async def _get_category_id(client: AsyncClient, headers: dict, name: str) -> str:
    resp = await client.get("/api/v1/categories", headers=headers)
    return next(c["id"] for c in resp.json() if c["name"] == name)


@pytest.mark.asyncio
async def test_create_transaction(client: AsyncClient, auth_headers: dict):
    category_id = await _get_category_id(client, auth_headers, "Food & Dining")
    resp = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": 25.5,
            "description": "Lunch",
            "category_id": category_id,
            "transaction_date": "2026-06-15",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["amount"] == 25.5
    assert body["category"]["name"] == "Food & Dining"


@pytest.mark.asyncio
async def test_create_transaction_rejects_negative_amount(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "expense", "amount": -10, "description": "Invalid", "transaction_date": "2026-06-15"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_transactions_pagination(client: AsyncClient, auth_headers: dict):
    for i in range(5):
        await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "type": "expense",
                "amount": 10 + i,
                "description": f"Item {i}",
                "transaction_date": "2026-06-15",
            },
        )
    resp = await client.get("/api/v1/transactions", headers=auth_headers, params={"page": 1, "page_size": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_list_transactions_filter_by_type(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "income", "amount": 1000, "description": "Salary", "transaction_date": "2026-06-01"},
    )
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "expense", "amount": 50, "description": "Groceries", "transaction_date": "2026-06-02"},
    )
    resp = await client.get("/api/v1/transactions", headers=auth_headers, params={"type": "income"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["type"] == "income"


@pytest.mark.asyncio
async def test_update_transaction(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "expense", "amount": 20, "description": "Coffee", "transaction_date": "2026-06-15"},
    )
    txn_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/transactions/{txn_id}", headers=auth_headers, json={"amount": 30, "description": "Coffee & Cake"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["amount"] == 30
    assert update_resp.json()["description"] == "Coffee & Cake"


@pytest.mark.asyncio
async def test_delete_transaction(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "expense", "amount": 20, "description": "Temp", "transaction_date": "2026-06-15"},
    )
    txn_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/transactions/{txn_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/transactions/{txn_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_bulk_delete_transactions(client: AsyncClient, auth_headers: dict):
    ids = []
    for i in range(3):
        resp = await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={"type": "expense", "amount": 5, "description": f"Bulk {i}", "transaction_date": "2026-06-15"},
        )
        ids.append(resp.json()["id"])

    resp = await client.post("/api/v1/transactions/bulk-delete", headers=auth_headers, json={"ids": ids})
    assert resp.status_code == 200
    assert resp.json()["deleted_count"] == 3


@pytest.mark.asyncio
async def test_transactions_are_isolated_per_user(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "expense", "amount": 5, "description": "User1 item", "transaction_date": "2026-06-15"},
    )
    await client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "full_name": "Other", "password": "strongpassword1"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "other@example.com", "password": "strongpassword1"}
    )
    other_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    resp = await client.get("/api/v1/transactions", headers=other_headers)
    assert resp.json()["total"] == 0
