import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.weather_service import WeatherService
from src.schemas.weather import CurrentWeather, Temperature, Wind, WeatherCondition
from datetime import datetime

@pytest.fixture
def mock_redis_service():
    """Mock Redis service for testing"""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    return redis_mock

@pytest.fixture
def weather_service(mock_redis_service):
    """Create a WeatherService instance with mocked dependencies"""
    service = WeatherService(redis_service=mock_redis_service)
    
    # Mock the external API methods
    service._get_open_meteo_current = AsyncMock()
    service._get_openweather_current = AsyncMock()
    service._get_weatherapi_current = AsyncMock()
    
    # Mock the _get_city_coordinates method to return valid coordinates
    service._get_city_coordinates = MagicMock(return_value={"lat": 48.8566, "lon": 2.3522})
    
    # Configure the mocks to return test data
    service._get_open_meteo_current.return_value = {
        "source": "open_meteo",
        "temperature": {
            "current": 20.5,
            "unit": "celsius"
        },
        "humidity": 65,
        "conditions": {
            "main": "Clouds",
            "description": "Partly cloudy"
        },
        "wind": {
            "speed": 10.0,
            "direction": 45.0,
            "unit": "m/s"
        }
    }
    
    service._get_openweather_current.return_value = {
        "source": "openweather",
        "temperature": {
            "current": 21.0,
            "unit": "celsius"
        },
        "humidity": 70,
        "conditions": {
            "main": "Clouds",
            "description": "Scattered clouds"
        },
        "wind": {
            "speed": 12.0,
            "direction": 90.0,
            "unit": "m/s"
        }
    }
    
    service._get_weatherapi_current.return_value = {
        "source": "weatherapi",
        "temperature": {
            "current": 20.0,
            "unit": "celsius"
        },
        "humidity": 68,
        "conditions": {
            "main": "Clouds",
            "description": "Partly cloudy"
        },
        "wind": {
            "speed": 11.0,
            "direction": 60.0,
            "unit": "m/s"
        }
    }
    
    return service

@pytest.mark.asyncio
async def test_get_current_weather_no_cache(weather_service, mock_redis_service):
    """Test getting current weather when no cache is available"""
    city = "Paris"
    
    # Ensure cache is empty
    mock_redis_service.get.return_value = None
    
    # Call the method
    result = await weather_service.get_current_weather(city)
    
    # Verify Redis get was called
    mock_redis_service.get.assert_called_once()
    
    # Verify the API methods were called
    weather_service._get_open_meteo_current.assert_called_once()
    weather_service._get_openweather_current.assert_called_once()
    weather_service._get_weatherapi_current.assert_called_once()
    
    # Verify the result is correct
    assert isinstance(result, CurrentWeather), f"Result is not a CurrentWeather object: {type(result)}"
    assert result.city == city, f"City mismatch: expected {city}, got {result.city}"
    
    # Debug sources
    print(f"Sources in result: {result.sources}")
    
    assert "open_meteo" in result.sources, f"open_meteo not in sources: {result.sources}"
    assert "openweather" in result.sources, f"openweather not in sources: {result.sources}"
    assert "weatherapi" in result.sources, f"weatherapi not in sources: {result.sources}"
    
    # Debug Redis set call
    print(f"Redis set called: {mock_redis_service.set.called}")
    print(f"Redis set call args: {mock_redis_service.set.call_args}")
    
    # Verify the result was cached
    mock_redis_service.set.assert_called_once()

@pytest.mark.asyncio
async def test_get_current_weather_with_cache(weather_service, mock_redis_service):
    """Test getting current weather when cache is available"""
    city = "Paris"
    
    # Set up cached data
    cached_weather = CurrentWeather(
        city=city,
        temperature=Temperature(current=22.0, unit="celsius"),
        conditions=WeatherCondition(main="Clear", description="Sunny"),
        humidity=60,
        wind=Wind(speed=10, direction=45.0, unit="m/s"),
        sources=["cache"],
        timestamp=datetime.now()
    )
    
    mock_redis_service.get.return_value = cached_weather.model_dump_json()
    
    # Call the method
    result = await weather_service.get_current_weather(city)
    
    # Verify Redis get was called
    mock_redis_service.get.assert_called_once()
    
    # Verify the API methods were NOT called
    weather_service._get_open_meteo_current.assert_not_called()
    weather_service._get_openweather_current.assert_not_called()
    weather_service._get_weatherapi_current.assert_not_called()
    
    # Verify the result is correct
    assert isinstance(result, CurrentWeather)
    assert result.city == city
    assert result.sources == ["cache"]

@pytest.mark.asyncio
async def test_get_current_weather_cache_error(weather_service, mock_redis_service):
    """Test getting current weather when cache read fails"""
    city = "Paris"
    
    # Set up the mock to raise an exception on get
    mock_redis_service.get.side_effect = Exception("Redis error")
    
    # Call the method
    result = await weather_service.get_current_weather(city)
    
    # Verify Redis get was called
    mock_redis_service.get.assert_called_once()
    
    # Debug API method calls
    print(f"_get_open_meteo_current called: {weather_service._get_open_meteo_current.called}")
    print(f"_get_openweather_current called: {weather_service._get_openweather_current.called}")
    print(f"_get_weatherapi_current called: {weather_service._get_weatherapi_current.called}")
    
    # Verify the API methods were called as fallback
    weather_service._get_open_meteo_current.assert_called_once()
    weather_service._get_openweather_current.assert_called_once()
    weather_service._get_weatherapi_current.assert_called_once()
    
    # Verify the result is correct (from API calls)
    assert isinstance(result, CurrentWeather), f"Result is not a CurrentWeather object: {type(result)}"
    assert result.city == city, f"City mismatch: expected {city}, got {result.city}"
    
    # Debug sources
    print(f"Sources in result: {result.sources}")
    
    assert "open_meteo" in result.sources, f"open_meteo not in sources: {result.sources}"
    assert "openweather" in result.sources, f"openweather not in sources: {result.sources}"

@pytest.mark.asyncio
async def test_get_current_weather_invalid_city(weather_service):
    """Test getting current weather for an invalid city"""
    city = "NonExistentCity"
    
    # Set up the service to return None for coordinates
    with patch.object(weather_service, '_get_city_coordinates', return_value=None):
        result = await weather_service.get_current_weather(city)
    
    # Verify the result is None
    assert result is None
