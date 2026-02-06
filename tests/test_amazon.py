"""Tests for Amazon SP-API integration endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app.core.auth import User, get_current_user
from app.db.session import engine, SessionLocal
from app.models.database import Base, UserSettings
from app.services.amazon_auth_service import AmazonAuthService, AmazonConnection
from app.services.amazon_sp_api_service import AmazonSPAPIService
from app.config import settings
from app.api.endpoints import amazon as amazon_endpoints


TEST_USER = User(id="user-test-123", email="test@example.com", role="authenticated")


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        Base.metadata.drop_all(bind=engine)


def test_amazon_auth_status_disconnected(client):
    response = client.get("/api/amazon/auth/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["connected"] is False
    assert payload["connection_mode"] == "none"


def test_amazon_auth_url_generation(client, monkeypatch):
    monkeypatch.setattr(settings, "amazon_spapi_app_id", "amzn1.sellerapps.app.test-app")
    monkeypatch.setattr(settings, "amazon_oauth_redirect_uri", "https://example.com/api/amazon/auth/callback")
    monkeypatch.setattr(settings, "amazon_oauth_version", "beta")

    response = client.post("/api/amazon/auth/url", json={"return_to": "/app/settings"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["auth_url"].startswith("https://sellercentral.amazon.com/apps/authorize/consent?")
    assert "application_id=amzn1.sellerapps.app.test-app" in payload["auth_url"]
    assert payload["expires_in_seconds"] == 600
    assert payload["state"]


def test_amazon_auth_callback_success_redirect(client, monkeypatch):
    db = SessionLocal()
    try:
        state = AmazonAuthService(db).create_signed_state(
            user_id=TEST_USER.id,
            marketplace_id="ATVPDKIKX0DER",
            return_to="/app/settings",
            expires_in_seconds=600,
        )
    finally:
        db.close()

    exchange_mock = AsyncMock(return_value={"refresh_token": "refresh-token-123"})
    save_calls = []

    async def fake_exchange(self, oauth_code):
        return await exchange_mock(oauth_code)

    def fake_save(self, *, user_id, refresh_token, seller_id, marketplace_id, email=None):
        save_calls.append(
            {
                "user_id": user_id,
                "refresh_token": refresh_token,
                "seller_id": seller_id,
                "marketplace_id": marketplace_id,
            }
        )

    monkeypatch.setattr(AmazonAuthService, "exchange_code_for_refresh_token", fake_exchange)
    monkeypatch.setattr(AmazonAuthService, "save_connection", fake_save)

    response = client.get(
        "/api/amazon/auth/callback",
        params={
            "spapi_oauth_code": "code-123",
            "state": state,
            "selling_partner_id": "A1SELLER123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "amazon_connect=success" in response.headers["location"]
    assert exchange_mock.await_count == 1
    assert save_calls and save_calls[0]["user_id"] == TEST_USER.id
    assert save_calls[0]["seller_id"] == "A1SELLER123"


def test_listing_push_creates_job_and_status_available(client, monkeypatch):
    async def noop_background(job_id: str):
        return None

    monkeypatch.setattr(amazon_endpoints, "_run_listing_push_job", noop_background)

    def fake_get_connection(self, user_id):
        return AmazonConnection(
            refresh_token="refresh-test",
            seller_id="A1SELLER123",
            marketplace_id="ATVPDKIKX0DER",
            mode="oauth",
            connected_at=None,
        )

    monkeypatch.setattr(AmazonAuthService, "get_connection", fake_get_connection)

    response = client.post(
        "/api/amazon/push/listing-images",
        json={
            "session_id": "session-123",
            "asin": "B012345678",
            "sku": "MY-SKU-1",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["job_id"]

    status_response = client.get(f"/api/amazon/push/status/{payload['job_id']}")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["job_id"] == payload["job_id"]
    assert status_payload["status"] == "queued"
    assert status_payload["kind"] == "listing_images"


def test_listing_push_accepts_sku_without_asin(client, monkeypatch):
    async def noop_background(job_id: str):
        return None

    monkeypatch.setattr(amazon_endpoints, "_run_listing_push_job", noop_background)

    def fake_get_connection(self, user_id):
        return AmazonConnection(
            refresh_token="refresh-test",
            seller_id="A1SELLER123",
            marketplace_id="ATVPDKIKX0DER",
            mode="oauth",
            connected_at=None,
        )

    monkeypatch.setattr(AmazonAuthService, "get_connection", fake_get_connection)

    response = client.post(
        "/api/amazon/push/listing-images",
        json={
            "session_id": "session-123",
            "sku": "MY-SKU-ONLY",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["job_id"]

    status_response = client.get(f"/api/amazon/push/status/{payload['job_id']}")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["asin"] is None
    assert status_payload["sku"] == "MY-SKU-ONLY"


def test_disconnect_clears_saved_connection(client):
    db = SessionLocal()
    try:
        row = UserSettings(
            user_id=TEST_USER.id,
            email=TEST_USER.email,
            amazon_refresh_token_encrypted="encrypted-token",
            amazon_seller_id="A1SELLER123",
            amazon_marketplace_id="ATVPDKIKX0DER",
        )
        db.add(row)
        db.commit()
    finally:
        db.close()

    response = client.delete("/api/amazon/auth/disconnect")
    assert response.status_code == 200
    assert response.json()["disconnected"] is True

    db = SessionLocal()
    try:
        saved = db.query(UserSettings).filter(UserSettings.user_id == TEST_USER.id).first()
        assert saved is not None
        assert saved.amazon_refresh_token_encrypted is None
        assert saved.amazon_seller_id is None
        assert saved.amazon_marketplace_id is None
    finally:
        db.close()


def test_list_skus_endpoint(client, monkeypatch):
    def fake_get_connection(self, user_id):
        return AmazonConnection(
            refresh_token="refresh-test",
            seller_id="A1SELLER123",
            marketplace_id="ATVPDKIKX0DER",
            mode="oauth",
            connected_at=None,
        )

    async def fake_refresh(self, refresh_token):
        return "access-token-123"

    async def fake_search(
        self,
        *,
        access_token,
        seller_id,
        marketplace_id,
        query=None,
        page_size=20,
    ):
        return {
            "skus": [
                {"sku": "SKU-001", "asin": "B012345678", "title": "Sample Item 1", "status": "BUYABLE"},
                {"sku": "SKU-002", "asin": "B076543210", "title": "Sample Item 2", "status": "DISCOVERABLE"},
            ],
            "next_token": None,
        }

    monkeypatch.setattr(AmazonAuthService, "get_connection", fake_get_connection)
    monkeypatch.setattr(AmazonAuthService, "refresh_access_token", fake_refresh)
    monkeypatch.setattr(AmazonSPAPIService, "search_listing_skus", fake_search)

    response = client.get("/api/amazon/skus", params={"query": "SKU", "limit": 10})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert payload["skus"][0]["sku"] == "SKU-001"
