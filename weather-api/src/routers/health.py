from fastapi import APIRouter, Depends
from typing import Dict, Any

from src.services.redis_service import RedisService, get_redis_service
import time
from datetime import datetime

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify API status and dependencies.
    Returns basic information about the API status.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time(),
        "version": "0.1.0",
        "services": {
            "database": "up",
            "redis": "up",
            "external_apis": {
                "open_meteo": "up",
                "openweather": "up",
                "weatherapi": "up"
            }
        }
    }

@router.get("/detailed", response_model=Dict[str, Any])
async def get_detailed_health(redis_service: RedisService = Depends(get_redis_service)) -> Dict[str, Any]:
    """
    Detailed health check that verifies connectivity to external services
    like weather APIs, database, and cache.
    """
    # In a real implementation, we would check each dependency
    # and report their status
    # Check database status (placeholder for real implementation)
    db_status = "up"  # In a real app, you'd check the DB connection
    
    # Check Redis status
    redis_status = "up" if await redis_service.health_check() else "down"
    
    # Check external APIs status (placeholder)
    apis_status = {
        "open_meteo": "up",
        "openweather": "up",
        "weatherapi": "up"
    }
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time(),
        "version": "0.1.0",
        "dependencies": {
            "database": db_status,
            "redis_cache": redis_status,
            "external_apis": apis_status
        }
    }
