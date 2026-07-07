"""Tests for registration, login, refresh, and protected-route access."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_creates_user_with_default_categories(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "full_name": "Alice", "password": "strongpassword1"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert "hashed_password" not in body


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client: AsyncClient):
    payload = {"email": "bob@example.com", "full_name": "Bob", "password": "strongpassword1"}
    first = await client.post("/api/v1/auth/register", json=payload)
    second = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_success_returns_token_pair(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "carol@example.com", "full_name": "Carol", "password": "strongpassword1"},
    )
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "carol@example.com", "password": "strongpassword1"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dave@example.com", "full_name": "Dave", "password": "strongpassword1"},
    )
    resp = await client.post("/api/v1/auth/login", json={"email": "dave@example.com", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_authentication(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_refresh_token_issues_new_access_token(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "erin@example.com", "full_name": "Erin", "password": "strongpassword1"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "erin@example.com", "password": "strongpassword1"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "frank@example.com", "full_name": "Frank", "password": "strongpassword1"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "frank@example.com", "password": "strongpassword1"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204

    reuse_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_resp.status_code == 401
