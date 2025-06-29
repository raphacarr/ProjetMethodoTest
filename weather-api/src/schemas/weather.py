from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class Temperature(BaseModel):
    current: float
    feels_like: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    unit: str = "celsius"

class Wind(BaseModel):
    speed: float
    direction: Optional[float] = None
    unit: str = "m/s"

class WeatherCondition(BaseModel):
    main: str
    description: str
    icon: Optional[str] = None

class CurrentWeather(BaseModel):
    city: str
    country: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    temperature: Temperature
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind: Optional[Wind] = None
    conditions: Optional[WeatherCondition] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[str] = []

class ForecastItem(BaseModel):
    timestamp: datetime
    temperature: Temperature
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind: Optional[Wind] = None
    conditions: Optional[WeatherCondition] = None
    precipitation_probability: Optional[float] = None

class Forecast(BaseModel):
    city: str
    country: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    forecast_items: List[ForecastItem]
    sources: List[str] = []

class HistoricalWeather(BaseModel):
    city: str
    country: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    historical_data: List[ForecastItem]
    sources: List[str] = []

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
