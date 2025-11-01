"""
In-memory cache backend implementation.

Useful for testing or development without Redis.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Tuple

from .base import CacheBackend

logger = logging.getLogger(__name__)


class MemoryBackend(CacheBackend):
    """
    In-memory cache backend.

    Stores cache data in a Python dictionary with TTL support.
    Useful for testing or when Redis is not available.
    """

    def __init__(self):
        """Initialize in-memory cache."""
        self._cache: Dict[str, Tuple[str, float]] = {}  # key -> (value, expiry_time)
        self._cleanup_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())
            logger.info("In-memory cache initialized")

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from memory cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        # Check if expired
        if time.time() > expiry:
            del self._cache[key]
            return None

        logger.debug(f"Memory cache hit: {key}")
        return value

    async def set(self, key: str, value: str, ttl: int) -> bool:
        """
        Set value in memory cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True (always successful)
        """
        expiry_time = time.time() + ttl
        self._cache[key] = (value, expiry_time)
        logger.debug(f"Memory cached: {key} (TTL: {ttl}s)")
        return True

    async def delete(self, key: str) -> bool:
        """
        Delete key from memory cache.

        Args:
            key: Cache key

        Returns:
            True if key existed
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted memory cache key: {key}")
            return True
        return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in memory cache.

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired
        """
        if key not in self._cache:
            return False

        _, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return False

        return True

    async def ping(self) -> bool:
        """
        Check memory cache health.

        Returns:
            True (always healthy)
        """
        return True

    async def close(self) -> None:
        """Clean up memory cache."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

        self._cache.clear()
        logger.info("Memory cache closed")

    async def _cleanup_expired(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute

                current_time = time.time()
                expired_keys = [
                    key
                    for key, (_, expiry) in self._cache.items()
                    if current_time > expiry
                ]

                for key in expired_keys:
                    del self._cache[key]

                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup task: {e}")


__all__ = ["MemoryBackend"]
