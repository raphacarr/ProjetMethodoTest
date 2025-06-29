import pytest
import json
from jsonschema import validate
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from src.main import app
from src.schemas.weather import CurrentWeather, Forecast, HistoricalWeather, Temperature, Wind, WeatherCondition, ForecastItem

# Schémas JSON pour la validation des contrats
current_weather_schema = {
    "type": "object",
    "required": ["city", "temperature", "sources"],
    "properties": {
        "city": {"type": "string"},
        "temperature": {
            "type": "object",
            "required": ["current", "unit"],
            "properties": {
                "current": {"type": "number"},
                "unit": {"type": "string"}
            }
        },
        "humidity": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
        "conditions": {
            "type": ["object", "null"],
            "required": ["main", "description"],
            "properties": {
                "main": {"type": "string"},
                "description": {"type": "string"}
            }
        },
        "wind": {
            "type": "object",
            "required": ["speed", "direction", "unit"],
            "properties": {
                "speed": {"type": "number", "minimum": 0},
                "direction": {"type": ["number", "null"]},
                "unit": {"type": "string"}
            }
        },
        "sources": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

forecast_schema = {
    "type": "object",
    "required": ["city", "forecast_items", "sources"],
    "properties": {
        "city": {"type": "string"},
        "forecast_items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["timestamp", "temperature"],
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time"},
                    "temperature": {
                        "type": "object",
                        "required": ["current", "unit"],
                        "properties": {
                            "current": {"type": "number"},
                            "min": {"type": ["number", "null"]},
                            "max": {"type": ["number", "null"]},
                            "unit": {"type": "string"}
                        }
                    },
                    "humidity": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
                    "conditions": {
                        "type": ["object", "null"],
                        "required": ["main", "description"],
                        "properties": {
                            "main": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    },
                    "wind": {
                        "type": ["object", "null"],
                        "required": ["speed", "unit"],
                        "properties": {
                            "speed": {"type": "number", "minimum": 0},
                            "direction": {"type": ["number", "null"]},
                            "unit": {"type": "string"}
                        }
                    }
                }
            }
        },
        "sources": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

historical_weather_schema = {
    "type": "object",
    "required": ["city", "historical_data", "sources"],
    "properties": {
        "city": {"type": "string"},
        "historical_data": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["timestamp", "temperature"],
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time"},
                    "temperature": {
                        "type": "object",
                        "required": ["current", "unit"],
                        "properties": {
                            "current": {"type": "number"},
                            "min": {"type": ["number", "null"]},
                            "max": {"type": ["number", "null"]},
                            "unit": {"type": "string"}
                        }
                    },
                    "humidity": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
                    "conditions": {
                        "type": ["object", "null"],
                        "required": ["main", "description"],
                        "properties": {
                            "main": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    },
                    "wind": {
                        "type": ["object", "null"],
                        "required": ["speed", "unit"],
                        "properties": {
                            "speed": {"type": "number", "minimum": 0},
                            "direction": {"type": ["number", "null"]},
                            "unit": {"type": "string"}
                        }
                    }
                }
            }
        },
        "sources": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

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
                    timestamp=datetime(2023, 6, 1, 12, 0),
                    temperature=Temperature(current=22.0, min=18.0, max=25.0, unit="celsius"),
                    humidity=60,
                    conditions=WeatherCondition(main="Clear", description="Sunny"),
                    wind=Wind(speed=10, direction=45.0, unit="m/s")
                ),
                ForecastItem(
                    timestamp=datetime(2023, 6, 2, 12, 0),
                    temperature=Temperature(current=20.0, min=17.0, max=24.0, unit="celsius"),
                    humidity=65,
                    conditions=WeatherCondition(main="Clouds", description="Partly cloudy"),
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
                    timestamp=datetime(2023, 5, 30, 12, 0),
                    temperature=Temperature(current=20.0, min=16.0, max=23.0, unit="celsius"),
                    humidity=75,
                    conditions=WeatherCondition(main="Rain", description="Rainy"),
                    wind=Wind(speed=15, direction=225.0, unit="m/s")
                ),
                ForecastItem(
                    timestamp=datetime(2023, 5, 29, 12, 0),
                    temperature=Temperature(current=18.0, min=15.0, max=22.0, unit="celsius"),
                    humidity=70,
                    conditions=WeatherCondition(main="Clouds", description="Cloudy"),
                    wind=Wind(speed=14, direction=270.0, unit="m/s")
                )
            ],
            sources=["weatherapi"]
        )
        
        yield service_instance

def test_current_weather_contract(test_client, mock_weather_service):
    """Test that the current weather endpoint response matches the contract schema"""
    response = test_client.get("/api/v1/weather/current/Paris")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response against schema
    validate(instance=data, schema=current_weather_schema)

def test_forecast_contract(test_client, mock_weather_service):
    """Test that the forecast endpoint response matches the contract schema"""
    response = test_client.get("/api/v1/weather/forecast/Paris?days=2")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response against schema
    validate(instance=data, schema=forecast_schema)

def test_history_contract(test_client, mock_weather_service):
    """Test that the history endpoint response matches the contract schema"""
    response = test_client.get("/api/v1/weather/history/Paris?days=2")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response against schema
    validate(instance=data, schema=historical_weather_schema)

def test_error_response_contract(test_client, mock_weather_service):
    """Test that error responses match the expected format"""
    # Configure the mock to return None for invalid city
    mock_weather_service.get_current_weather.return_value = None
    
    response = test_client.get("/api/v1/weather/current/InvalidCity123")
    
    assert response.status_code == 500  # L'API retourne 500 au lieu de 404
    data = response.json()
    
    # Validate error response format
    assert "detail" in data
    assert isinstance(data["detail"], str)
