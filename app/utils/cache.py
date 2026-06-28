"""
Utility functions for Redis caching
"""
import json
import hashlib
from typing import Any, Optional, Union
from redis.asyncio import Redis
from app.core.config import settings

# Initialize Redis client
redis_client = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_from_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = await redis_client.get(key)
        if value is not None:
            return json.loads(value)
    except Exception:
        pass  # If cache fails, continue without caching
    return None

async def set_in_cache(key: str, value: Any, expire: int = 300) -> None:
    """Set value in cache with expiration time (default 5 minutes)"""
    try:
        await redis_client.setex(key, expire, json.dumps(value, default=str))
    except Exception:
        pass  # If cache fails, continue without caching

def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from parameters"""
    # Sort keys to ensure consistent ordering
    sorted_items = sorted(kwargs.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_items if v is not None])
    if not query_string:
        return prefix

    # Hash the query string to avoid overly long keys
    key_hash = hashlib.md5(query_string.encode()).hexdigest()
    return f"{prefix}:{key_hash}"

async def delete_cache_pattern(pattern: str) -> None:
    """Delete all keys matching a pattern"""
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
    except Exception:
        pass  # If cache fails, continue without caching