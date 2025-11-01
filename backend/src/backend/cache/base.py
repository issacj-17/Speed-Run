"""
Abstract base classes for cache layer.

This allows easy swapping between Redis, Memcached, or in-memory cache.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheBackend(ABC):
    """
    Abstract cache backend interface.

    Implement this interface to create new cache backends
    (Redis, Memcached, in-memory, Supabase cache, etc.)
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value as string or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (as string)
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """
        Check if cache backend is healthy.

        Returns:
            True if backend is reachable
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connection to cache backend."""
        pass


__all__ = ["CacheBackend"]
