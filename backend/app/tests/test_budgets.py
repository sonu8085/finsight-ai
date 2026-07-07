"""Tests for budget creation and spend-vs-limit progress calculation."""
import pytest
from httpx import AsyncClient


async def _get_category_id(client: AsyncClient, headers: dict, name: str) -> str:
    resp = await client.get("/api/v1/categories", headers=headers)
    return next(c["id"] for c in resp.json() if c["name"] == name)


@pytest.mark.asyncio
async def test_create_and_track_budget_progress(client: AsyncClient, auth_headers: dict):
    category_id = await _get_category_id(client, auth_headers, "Groceries")

    await client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={"category_id": category_id, "period": "monthly", "amount_limit": 200, "month": 6, "year": 2026},
    )
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": 80,
            "description": "Weekly shop",
            "category_id": category_id,
            "transaction_date": "2026-06-10",
        },
    )

    resp = await client.get("/api/v1/budgets", headers=auth_headers, params={"month": 6, "year": 2026})
    assert resp.status_code == 200
    budgets = resp.json()
    assert len(budgets) == 1
    assert budgets[0]["spent"] == 80
    assert budgets[0]["remaining"] == 120
    assert budgets[0]["utilization_pct"] == 40.0


@pytest.mark.asyncio
async def test_budget_excludes_other_categories(client: AsyncClient, auth_headers: dict):
    groceries_id = await _get_category_id(client, auth_headers, "Groceries")
    transport_id = await _get_category_id(client, auth_headers, "Transport")

    await client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={"category_id": groceries_id, "period": "monthly", "amount_limit": 100, "month": 6, "year": 2026},
    )
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": 50,
            "description": "Gas",
            "category_id": transport_id,
            "transaction_date": "2026-06-10",
        },
    )

    resp = await client.get("/api/v1/budgets", headers=auth_headers, params={"month": 6, "year": 2026})
    assert resp.json()[0]["spent"] == 0


@pytest.mark.asyncio
async def test_update_budget_limit(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={"period": "monthly", "amount_limit": 500, "month": 7, "year": 2026},
    )
    budget_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/budgets/{budget_id}", headers=auth_headers, json={"amount_limit": 750}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["amount_limit"] == 750


@pytest.mark.asyncio
async def test_delete_budget(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={"period": "monthly", "amount_limit": 500, "month": 8, "year": 2026},
    )
    budget_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    list_resp = await client.get("/api/v1/budgets", headers=auth_headers, params={"month": 8, "year": 2026})
    assert list_resp.json() == []
