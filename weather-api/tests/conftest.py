import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import asyncio

from src.main import app
from src.services.weather_service import WeatherService

@pytest.fixture
def test_client():
    """Return a TestClient instance for testing the API endpoints"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_weather_service():
    """Mock the WeatherService to avoid real API calls during tests"""
    with patch("src.routers.weather.WeatherService") as mock_service:
        # Configure the mock to return test data
        service_instance = MagicMock(spec=WeatherService)
        mock_service.return_value = service_instance
        yield service_instance

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
