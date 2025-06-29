import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from fastapi import Depends

from src.middleware.prometheus import track_external_api_call
from src.services.redis_service import RedisService, get_redis_service

from config.settings import settings
from src.schemas.weather import CurrentWeather, Forecast, HistoricalWeather, Temperature, Wind, WeatherCondition, ForecastItem

class WeatherService:
    def __init__(self, redis_service: RedisService = Depends(get_redis_service)):
        self.open_meteo_base_url = settings.OPEN_METEO_BASE_URL
        self.openweather_api_key = settings.OPENWEATHER_API_KEY
        self.weatherapi_key = settings.WEATHERAPI_KEY
        self.redis_service = redis_service
        
        # Simple city coordinates mapping for testing
        # In a real app, you'd use a geocoding service
        self.city_coordinates = {
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "london": {"lat": 51.5074, "lon": -0.1278},
            "new york": {"lat": 40.7128, "lon": -74.0060},
            "tokyo": {"lat": 35.6762, "lon": 139.6503},
            "sydney": {"lat": -33.8688, "lon": 151.2093},
            "berlin": {"lat": 52.5200, "lon": 13.4050},
            "madrid": {"lat": 40.4168, "lon": -3.7038},
            "rome": {"lat": 41.9028, "lon": 12.4964},
        }
    
    def _get_city_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a city from our simple mapping"""
        return self.city_coordinates.get(city.lower())
    
    async def get_current_weather(self, city: str) -> Optional[CurrentWeather]:
        """
        Get current weather for a city by aggregating data from multiple sources
        """
        # Try to get from cache first
        cache_key = f"weather:current:{city.lower()}"
        try:
            cached_data = await self.redis_service.get(cache_key)
            if cached_data:
                try:
                    return CurrentWeather.model_validate_json(cached_data)
                except Exception as e:
                    print(f"Cache parsing error: {e}")
                    # Continue if parsing fails
                    pass
        except Exception as e:
            print(f"Cache read error: {e}")
            # Continue if cache read fails
            pass
                
        coords = self._get_city_coordinates(city)
        print(f"Coordinates for {city}: {coords}")
        if not coords:
            print(f"No coordinates found for {city}")
            return None
        
        # Call all weather APIs concurrently
        tasks = [
            self._get_open_meteo_current(city, coords),
            self._get_openweather_current(city),
            self._get_weatherapi_current(city)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"API results: {results}")
        
        # Filter out exceptions and None results
        valid_results = []
        for result in results:
            if not isinstance(result, Exception) and result is not None:
                valid_results.append(result)
            elif isinstance(result, Exception):
                print(f"API error: {result}")
        
        print(f"Valid results: {valid_results}")
        
        # Aggregate the results
        result = self._aggregate_current_weather(valid_results, city, coords)
        print(f"Aggregated result: {result}")
        
        # Cache the result if we have valid data
        if result and valid_results:
            # No try/except here to let the test verify the call
            try:
                await self.redis_service.set(
                    cache_key,
                    result.model_dump_json(),
                    ex=300  # Cache for 5 minutes
                )
                print(f"Result cached with key {cache_key}")
            except Exception as e:
                print(f"Cache write error: {e}")
        
        return result
    
    async def _get_open_meteo_current(self, city: str, coords: Dict[str, float]) -> Dict[str, Any]:
        """Get current weather from Open-Meteo API"""
        async with httpx.AsyncClient() as client:
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current_weather": "true",
                "hourly": "temperature_2m,relativehumidity_2m,pressure_msl,windspeed_10m,winddirection_10m"
            }
            
            try:
                response = await client.get(f"{self.open_meteo_base_url}/forecast", params=params)
                response.raise_for_status()
                data = response.json()
                # Track successful API call
                track_external_api_call("open_meteo", success=True)
            except Exception as e:
                # Track failed API call
                track_external_api_call("open_meteo", success=False)
                raise e
            
            # Extract current hour data from hourly data
            current_hour_index = 0  # For simplicity, use first hour
            
            return {
                "source": "open_meteo",
                "temperature": {
                    "current": data["current_weather"]["temperature"],
                    "unit": "celsius"
                },
                "humidity": data["hourly"]["relativehumidity_2m"][current_hour_index] if "relativehumidity_2m" in data["hourly"] else None,
                "wind": {
                    "speed": data["current_weather"]["windspeed"],
                    "direction": data["current_weather"]["winddirection"],
                    "unit": "km/h"
                },
                "conditions": {
                    "main": self._get_weather_condition_from_code(data["current_weather"]["weathercode"]),
                    "description": self._get_weather_description_from_code(data["current_weather"]["weathercode"])
                }
            }
    
    async def _get_openweather_current(self, city: str) -> Dict[str, Any]:
        """Get current weather from OpenWeatherMap API"""
        if not self.openweather_api_key:
            return None
            
        async with httpx.AsyncClient() as client:
            params = {
                "q": city,
                "appid": self.openweather_api_key,
                "units": "metric"
            }
            
            try:
                response = await client.get("https://api.openweathermap.org/data/2.5/weather", params=params)
                response.raise_for_status()
                data = response.json()
                # Track successful API call
                track_external_api_call("openweather", success=True)
            except Exception as e:
                # Track failed API call
                track_external_api_call("openweather", success=False)
                raise e
            
            return {
                "source": "openweather",
                "temperature": {
                    "current": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "min": data["main"]["temp_min"],
                    "max": data["main"]["temp_max"],
                    "unit": "celsius"
                },
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind": {
                    "speed": data["wind"]["speed"],
                    "direction": data["wind"].get("deg"),
                    "unit": "m/s"
                },
                "conditions": {
                    "main": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"]
                }
            }
    
    async def _get_weatherapi_current(self, city: str) -> Dict[str, Any]:
        """Get current weather from WeatherAPI.com"""
        if not self.weatherapi_key:
            return None
            
        async with httpx.AsyncClient() as client:
            params = {
                "q": city,
                "key": self.weatherapi_key
            }
            
            try:
                response = await client.get("https://api.weatherapi.com/v1/current.json", params=params)
                response.raise_for_status()
                data = response.json()
                # Track successful API call
                track_external_api_call("weatherapi", success=True)
            except Exception as e:
                # Track failed API call
                track_external_api_call("weatherapi", success=False)
                raise e
            
            return {
                "source": "weatherapi",
                "temperature": {
                    "current": data["current"]["temp_c"],
                    "feels_like": data["current"]["feelslike_c"],
                    "unit": "celsius"
                },
                "humidity": data["current"]["humidity"],
                "pressure": data["current"]["pressure_mb"],
                "wind": {
                    "speed": data["current"]["wind_kph"],
                    "direction": data["current"]["wind_degree"],
                    "unit": "km/h"
                },
                "conditions": {
                    "main": data["current"]["condition"]["text"],
                    "description": data["current"]["condition"]["text"],
                    "icon": data["current"]["condition"]["icon"]
                }
            }
    
    def _aggregate_current_weather(self, results: List[Dict[str, Any]], city: str, coords: Dict[str, float]) -> Optional[CurrentWeather]:
        """Aggregate weather data from multiple sources"""
        if not results:
            print("No valid results to aggregate")
            return None
            
        # Calculate average temperature
        temps = [r["temperature"]["current"] for r in results if "temperature" in r]
        avg_temp = sum(temps) / len(temps) if temps else None
        
        if avg_temp is None:
            print("No temperature data available")
            return None
        
        # Get humidity average
        humidities = [r["humidity"] for r in results if "humidity" in r and r["humidity"] is not None]
        avg_humidity = sum(humidities) / len(humidities) if humidities else None
        
        # Get wind speed average (note: would need to normalize units in real app)
        wind_speeds = [r["wind"]["speed"] for r in results if "wind" in r and r["wind"] is not None]
        avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else None
        
        # Get a representative weather condition (using the first one for simplicity)
        condition = next((r["conditions"] for r in results if "conditions" in r), None)
        
        # Get sources
        sources = [r["source"] for r in results]
        
        # Create aggregated weather data
        weather_condition = None
        if condition:
            weather_condition = WeatherCondition(
                main=condition.get("main", "Unknown"),
                description=condition.get("description", "Unknown")
            )
            
        wind = None
        if avg_wind_speed is not None:
            wind = Wind(
                speed=avg_wind_speed,
                direction=next((r["wind"]["direction"] for r in results if "wind" in r and "direction" in r["wind"]), None),
                unit="m/s"  # Simplified, would need proper unit conversion
            )
        
        try:
            current_weather = CurrentWeather(
                city=city,
                coordinates=coords,
                temperature=Temperature(
                    current=avg_temp,
                    unit="celsius"
                ),
                humidity=avg_humidity,
                conditions=weather_condition,
                wind=wind,
                timestamp=datetime.now(),
                sources=sources
            )
            return current_weather
        except Exception as e:
            print(f"Error creating CurrentWeather object: {e}")
            return None
    
    def _get_weather_condition_from_code(self, code: int) -> str:
        """Convert Open-Meteo weather code to condition string"""
        # Simplified mapping
        if code < 3:
            return "Clear"
        elif code < 50:
            return "Clouds"
        elif code < 70:
            return "Rain"
        elif code < 80:
            return "Snow"
        else:
            return "Thunderstorm"
    
    def _get_weather_description_from_code(self, code: int) -> str:
        """Convert Open-Meteo weather code to description string"""
        # Simplified mapping
        codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            95: "Thunderstorm"
        }
        return codes.get(code, "Unknown")
    
    async def get_forecast(self, city: str, days: int = 5) -> Optional[Forecast]:
        """Get weather forecast for a city"""
        # This would be implemented similarly to get_current_weather
        # For now, we'll return a placeholder
        coords = self._get_city_coordinates(city)
        if not coords:
            return None
            
        # In a real implementation, we would call the forecast endpoints
        # of our weather APIs and aggregate the results
        
        # Placeholder implementation
        forecast_items = []
        for i in range(days):
            future_date = datetime.now() + timedelta(days=i)
            forecast_items.append(
                ForecastItem(
                    timestamp=future_date,
                    temperature=Temperature(
                        current=20.0 + i,  # Placeholder temperature
                        unit="celsius"
                    ),
                    humidity=70.0 - i,
                    conditions=WeatherCondition(
                        main="Clear",
                        description="Clear sky"
                    )
                )
            )
            
        return Forecast(
            city=city,
            coordinates=coords,
            forecast_items=forecast_items,
            sources=["placeholder"]
        )
    
    async def get_history(self, city: str, days: int = 5) -> Optional[HistoricalWeather]:
        """Get historical weather data for a city"""
        # This would be implemented similarly to get_forecast
        # For now, we'll return a placeholder
        coords = self._get_city_coordinates(city)
        if not coords:
            return None
            
        # Placeholder implementation
        historical_data = []
        for i in range(days):
            past_date = datetime.now() - timedelta(days=i+1)
            historical_data.append(
                ForecastItem(
                    timestamp=past_date,
                    temperature=Temperature(
                        current=20.0 - i,  # Placeholder temperature
                        unit="celsius"
                    ),
                    humidity=70.0 + i,
                    conditions=WeatherCondition(
                        main="Clouds",
                        description="Scattered clouds"
                    )
                )
            )
            
        return HistoricalWeather(
            city=city,
            coordinates=coords,
            historical_data=historical_data,
            sources=["placeholder"]
        )
