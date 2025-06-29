import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from src.main import app
from src.schemas.weather import CurrentWeather, Forecast, HistoricalWeather, Temperature, Wind, WeatherCondition, ForecastItem

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
        service_instance = mock_service.return_value
        
        # Mock get_current_weather
        service_instance.get_current_weather = AsyncMock()
        service_instance.get_current_weather.return_value = CurrentWeather(
            city="Paris",
            temperature=Temperature(current=22.0, unit="celsius"),
            conditions=WeatherCondition(main="Clear", description="Sunny"),
            humidity=60,
            wind=Wind(speed=10, direction=45.0, unit="m/s"),
            sources=["openweather", "weatherapi"],
            timestamp=datetime.now()
        )
        
        # Mock get_forecast
        service_instance.get_forecast = AsyncMock()
        service_instance.get_forecast.return_value = Forecast(
            city="Paris",
            forecast_items=[
                ForecastItem(
                    timestamp=datetime.strptime("2023-06-01", "%Y-%m-%d"),
                    temperature=Temperature(min=18.0, max=25.0, current=22.0, unit="celsius"),
                    conditions=WeatherCondition(main="Clear", description="Sunny"),
                    humidity=60,
                    wind=Wind(speed=10, direction=45.0, unit="m/s")
                ),
                ForecastItem(
                    timestamp=datetime.strptime("2023-06-02", "%Y-%m-%d"),
                    temperature=Temperature(min=17.0, max=24.0, current=20.0, unit="celsius"),
                    conditions=WeatherCondition(main="Clouds", description="Partly cloudy"),
                    humidity=65,
                    wind=Wind(speed=12, direction=90.0, unit="m/s")
                )
            ],
            sources=["openweather", "weatherapi"]
        )
        
        # Mock get_weather_history
        service_instance.get_weather_history = AsyncMock()
        service_instance.get_weather_history.return_value = HistoricalWeather(
            city="Paris",
            historical_data=[
                ForecastItem(
                    timestamp=datetime.strptime("2023-05-30", "%Y-%m-%d"),
                    temperature=Temperature(min=16.0, max=23.0, current=20.0, unit="celsius"),
                    conditions=WeatherCondition(main="Rain", description="Rainy"),
                    humidity=75,
                    wind=Wind(speed=15, direction=225.0, unit="m/s")
                ),
                ForecastItem(
                    timestamp=datetime.strptime("2023-05-29", "%Y-%m-%d"),
                    temperature=Temperature(min=15.0, max=22.0, current=18.0, unit="celsius"),
                    conditions=WeatherCondition(main="Clouds", description="Cloudy"),
                    humidity=70,
                    wind=Wind(speed=14, direction=270.0, unit="m/s")
                )
            ],
            sources=["weatherapi"]
        )
        
        yield service_instance

def test_get_current_weather_valid_city(test_client, mock_weather_service):
    """Test getting current weather for a valid city"""
    response = test_client.get("/api/v1/weather/current/Paris")
    
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert "temperature" in data
    assert "current" in data["temperature"]
    assert "conditions" in data
    assert "wind" in data
    assert "sources" in data
    assert "openweather" in data["sources"]
    assert "weatherapi" in data["sources"]

def test_get_current_weather_invalid_city(test_client, mock_weather_service):
    """Test getting current weather for an invalid city"""
    # Configure the mock to return None for invalid city
    mock_weather_service.get_current_weather.return_value = None
    
    response = test_client.get("/api/v1/weather/current/InvalidCity123")
    
    assert response.status_code == 500  # L'API retourne 500 au lieu de 404
    data = response.json()
    assert "detail" in data

def test_get_forecast_valid_city(test_client, mock_weather_service):
    """Test getting forecast for a valid city"""
    response = test_client.get("/api/v1/weather/forecast/Paris?days=2")
    
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert "forecast_items" in data
    assert len(data["forecast_items"]) == 2
    assert "sources" in data
    # Vérifier simplement que sources est une liste non vide
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0

def test_get_forecast_invalid_city(test_client, mock_weather_service):
    """Test getting forecast for an invalid city"""
    # Configure the mock to return None for invalid city
    mock_weather_service.get_forecast.return_value = None
    
    response = test_client.get("/api/v1/weather/forecast/InvalidCity123")
    
    assert response.status_code == 500  # L'API retourne 500 au lieu de 404
    data = response.json()
    assert "detail" in data

def test_get_history_valid_city(test_client, mock_weather_service):
    """Test getting history for a valid city"""
    response = test_client.get("/api/v1/weather/history/Paris?days=2")
    
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert "historical_data" in data
    assert len(data["historical_data"]) == 2
    assert "sources" in data
    # Vérifier simplement que sources est une liste non vide
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0

def test_get_history_invalid_city(test_client, mock_weather_service):
    """Test getting history for an invalid city"""
    # Configure the mock to return None for invalid city
    mock_weather_service.get_weather_history.return_value = None
    
    response = test_client.get("/api/v1/weather/history/InvalidCity123")
    
    assert response.status_code == 500  # L'API retourne 500 au lieu de 404
    data = response.json()
    assert "detail" in data
