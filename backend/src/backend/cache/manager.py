"""
Cache manager with dependency injection support.

Allows easy swapping between Redis, Memcached, in-memory, or custom cache backends.
"""

import logging
from typing import Optional

from .base import CacheBackend
from .redis_backend import RedisBackend
from .memory_backend import MemoryBackend
from backend.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Cache manager using dependency injection.

    Supports multiple cache backends (Redis, in-memory, etc.)
    """

    def __init__(self, backend: Optional[CacheBackend] = None):
        """
        Initialize cache manager with a backend.

        Args:
            backend: Cache backend implementation (defaults to Redis or memory)
        """
        self._backend = backend
        self._initialized = False

    async def init(self) -> None:
        """Initialize cache backend."""
        if self._backend is None:
            # Default to Redis if enabled, otherwise use in-memory
            if settings.CACHE_ENABLED:
                try:
                    self._backend = RedisBackend()
                    await self._backend.connect()
                    # Test connection
                    if not await self._backend.ping():
                        raise RuntimeError("Redis ping failed")
                    logger.info("Cache manager initialized with Redis backend")
                except Exception as e:
                    logger.warning(f"Redis connection failed: {e}. Falling back to in-memory cache.")
                    self._backend = MemoryBackend()
                    await self._backend.connect()
            else:
                logger.info("Cache disabled in settings")
                self._backend = MemoryBackend()
                await self._backend.connect()
        else:
            # Custom backend provided
            await self._backend.connect()
            logger.info(f"Cache manager initialized with custom backend: {type(self._backend).__name__}")

        self._initialized = True

    async def close(self) -> None:
        """Close cache backend."""
        if self._backend:
            await self._backend.close()
        self._initialized = False

    @property
    def backend(self) -> CacheBackend:
        """Get cache backend."""
        if not self._initialized or self._backend is None:
            raise RuntimeError("Cache manager not initialized. Call init() first.")
        return self._backend

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self.backend.get(key)

    async def set(self, key: str, value: str, ttl: int) -> bool:
        """Set value in cache with TTL."""
        return await self.backend.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return await self.backend.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self.backend.exists(key)

    async def health_check(self) -> bool:
        """Check cache backend health."""
        if not self._initialized or self._backend is None:
            return False
        return await self.backend.ping()


# Global cache manager instance
cache_manager = CacheManager()


async def init_cache(backend: Optional[CacheBackend] = None) -> CacheManager:
    """
    Initialize cache manager.

    Args:
        backend: Optional custom cache backend

    Returns:
        Initialized cache manager
    """
    global cache_manager
    if backend:
        cache_manager = CacheManager(backend)
    await cache_manager.init()
    return cache_manager


async def close_cache() -> None:
    """Close cache manager."""
    await cache_manager.close()


async def get_cache() -> CacheManager:
    """
    Get cache manager instance (for FastAPI dependency injection).

    Returns:
        Cache manager instance
    """
    return cache_manager


__all__ = ["CacheManager", "cache_manager", "init_cache", "close_cache", "get_cache"]
