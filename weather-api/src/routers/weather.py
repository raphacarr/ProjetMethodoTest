from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from src.schemas.weather import CurrentWeather, Forecast, HistoricalWeather, ErrorResponse
from src.services.weather_service import WeatherService

router = APIRouter(
    prefix="/weather",
    tags=["weather"],
    responses={404: {"model": ErrorResponse}}
)

@router.get("/current/{city}", response_model=CurrentWeather)
async def get_current_weather(
    city: str,
    service: WeatherService = Depends()
):
    """
    Get current weather data for a specific city.
    """
    try:
        result = await service.get_current_weather(city)
        if not result:
            raise HTTPException(status_code=404, detail=f"Weather data for city '{city}' not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{city}", response_model=Forecast)
async def get_weather_forecast(
    city: str,
    days: Optional[int] = Query(5, ge=1, le=10),
    service: WeatherService = Depends()
):
    """
    Get weather forecast for a specific city for the next X days (default 5).
    """
    try:
        result = await service.get_forecast(city, days)
        if not result:
            raise HTTPException(status_code=404, detail=f"Forecast data for city '{city}' not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{city}", response_model=HistoricalWeather)
async def get_weather_history(
    city: str,
    days: Optional[int] = Query(5, ge=1, le=30),
    service: WeatherService = Depends()
):
    """
    Get historical weather data for a specific city for the past X days (default 5).
    """
    try:
        result = await service.get_history(city, days)
        if not result:
            raise HTTPException(status_code=404, detail=f"Historical data for city '{city}' not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
