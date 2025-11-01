"""
Redis implementation of cache backend.

This can be easily swapped with other implementations (Memcached, in-memory, etc.)
"""

import logging
from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

from .base import CacheBackend
from backend.config import settings

logger = logging.getLogger(__name__)


class RedisBackend(CacheBackend):
    """
    Redis cache backend implementation.

    Uses async Redis client for non-blocking operations.
    """

    def __init__(self, redis_url: str = None, max_connections: int = None):
        """
        Initialize Redis backend.

        Args:
            redis_url: Redis connection URL (defaults to settings)
            max_connections: Max connections in pool (defaults to settings)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.max_connections = max_connections or settings.REDIS_MAX_CONNECTIONS
        self._client: Optional[Redis] = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        if self._client is None:
            self._client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.max_connections,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            )
            logger.info(f"Redis client connected: {self.redis_url}")

    @property
    def client(self) -> Redis:
        """Get Redis client (lazy initialization)."""
        if self._client is None:
            raise RuntimeError("Redis client not initialized. Call connect() first.")
        return self._client

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
            return value
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int) -> bool:
        """
        Set value in Redis with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            await self.client.setex(key, ttl, value)
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            result = await self.client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            result = await self.client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    async def ping(self) -> bool:
        """
        Check Redis health.

        Returns:
            True if Redis is reachable
        """
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("Redis connection closed")


__all__ = ["RedisBackend"]
