import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Weather API"
    
    # External Weather APIs
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    WEATHERAPI_KEY: Optional[str] = os.getenv("WEATHERAPI_KEY")
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/weather_db")
    
    # Redis cache
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Cache settings
    CACHE_EXPIRATION: int = 600  # 10 minutes in seconds
    
    # Server settings
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
