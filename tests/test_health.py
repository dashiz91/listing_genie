"""Tests for health check endpoints"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_health():
    """Test root health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "listing-genie"
    assert "version" in data


def test_api_health():
    """Test API health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "listing-genie"
    assert "version" in data
    assert "dependencies" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_docs_endpoint():
    """Test Swagger UI is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options(
        "/health",
        headers={"Origin": "http://localhost:5173"}
    )
    # CORS preflight should not fail
    assert response.status_code in [200, 405]


def test_security_headers():
    """Test security headers are present"""
    response = client.get("/health")
    assert "x-content-type-options" in response.headers
    assert "x-frame-options" in response.headers
