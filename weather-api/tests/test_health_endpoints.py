import pytest
from fastapi.testclient import TestClient

from src.main import app

@pytest.fixture
def test_client():
    """Return a TestClient instance for testing the API endpoints"""
    with TestClient(app) as client:
        yield client

def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/api/v1/health/")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    
    # Check that the response includes service statuses
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]
    assert "external_apis" in data["services"]

def test_root_endpoint(test_client):
    """Test the root endpoint"""
    response = test_client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Welcome" in data["message"]
