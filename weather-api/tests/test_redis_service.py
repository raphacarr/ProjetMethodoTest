import pytest
import json
from unittest.mock import AsyncMock, patch
from src.services.redis_service import RedisService

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    return redis_mock

@pytest.fixture
def redis_service(mock_redis_client):
    """Create a RedisService instance with a mocked Redis client"""
    with patch("src.services.redis_service.redis.from_url", return_value=mock_redis_client):
        service = RedisService()
        service.redis = mock_redis_client
        yield service

@pytest.mark.asyncio
async def test_get_nonexistent_key(redis_service, mock_redis_client):
    """Test getting a nonexistent key from Redis"""
    mock_redis_client.get.return_value = None
    
    result = await redis_service.get("nonexistent_key")
    
    assert result is None
    mock_redis_client.get.assert_called_once_with("nonexistent_key")

@pytest.mark.asyncio
async def test_get_existing_key(redis_service, mock_redis_client):
    """Test getting an existing key from Redis"""
    test_data = json.dumps({"test": "data"})
    mock_redis_client.get.return_value = test_data
    
    result = await redis_service.get("existing_key")
    
    assert result == test_data
    mock_redis_client.get.assert_called_once_with("existing_key")

@pytest.mark.asyncio
async def test_set_key(redis_service, mock_redis_client):
    """Test setting a key in Redis"""
    key = "test_key"
    value = "test_value"
    expiration = 300
    
    await redis_service.set(key, value, ex=expiration)
    
    mock_redis_client.set.assert_called_once_with(key, value, ex=expiration)

@pytest.mark.asyncio
async def test_delete_key(redis_service, mock_redis_client):
    """Test deleting a key from Redis"""
    key = "test_key"
    
    await redis_service.delete(key)
    
    mock_redis_client.delete.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_redis_connection_error(mock_redis_client):
    """Test handling Redis connection error"""
    # Mock Redis client to raise an exception when connecting
    with patch("src.services.redis_service.redis.from_url", side_effect=Exception("Connection error")):
        # The service should handle the connection error gracefully
        service = RedisService()
        
        # The service should still be usable, but operations will fail
        assert await service.get_redis() is None
        
        # Test that operations handle the None client gracefully
        result = await service.get("some_key")
        assert result is None
