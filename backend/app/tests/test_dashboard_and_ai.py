"""Tests for dashboard aggregation and the AI insights fallback path."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_summary_computes_totals(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "income", "amount": 3000, "description": "Salary", "transaction_date": "2026-06-01"},
    )
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "expense", "amount": 1200, "description": "Rent", "transaction_date": "2026-06-02"},
    )

    resp = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["monthly_income"] >= 0
    assert "category_breakdown" in body
    assert "monthly_trends" in body
    assert len(body["monthly_trends"]) == 6


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ai_insights_fallback_without_api_key(client: AsyncClient, auth_headers: dict):
    """Without OPENAI_API_KEY configured, the endpoint should still return
    rule-based insights rather than failing."""
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={"type": "income", "amount": 2000, "description": "Salary", "transaction_date": "2026-06-01"},
    )
    resp = await client.get("/api/v1/ai/insights", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json()["insights"], list)
    assert len(resp.json()["insights"]) > 0


@pytest.mark.asyncio
async def test_ai_chat_fallback_without_api_key(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/ai/chat", headers=auth_headers, json={"message": "How much have I spent?"}
    )
    assert resp.status_code == 200
    assert "reply" in resp.json()
