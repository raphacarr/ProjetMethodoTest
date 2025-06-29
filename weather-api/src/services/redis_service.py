import redis.asyncio as redis
from typing import Optional, Any
import json
from fastapi import Depends

from config.settings import settings

class RedisService:
    def __init__(self):
        """Initialize Redis connection if URL is provided in settings"""
        self.redis_url = settings.REDIS_URL
        self._redis_client = None
        
    async def get_redis(self) -> Optional[redis.Redis]:
        """Get or create Redis client"""
        if not self.redis_url:
            return None
            
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
                # Test connection
                await self._redis_client.ping()
            except Exception as e:
                print(f"Redis connection error: {e}")
                self._redis_client = None
                
        return self._redis_client
        
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        client = await self.get_redis()
        if not client:
            return None
            
        try:
            return await client.get(key)
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
            
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration in seconds"""
        client = await self.get_redis()
        if not client:
            return False
            
        try:
            await client.set(key, value, ex=ex)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        client = await self.get_redis()
        if not client:
            return False
            
        try:
            await client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
            
    async def health_check(self) -> bool:
        """Check if Redis is healthy"""
        client = await self.get_redis()
        if not client:
            return False
            
        try:
            await client.ping()
            return True
        except Exception:
            return False

# Singleton instance
redis_service = RedisService()

# Dependency for FastAPI
async def get_redis_service() -> RedisService:
    return redis_service
