"""
Redis cache layer for Speed-Run AML Platform.

This cache layer uses dependency injection to allow easy swapping
between Redis, Memcached, in-memory, or custom cache backends.

Quick Start:
    # In your FastAPI app startup
    from cache import init_cache, close_cache

    @app.on_event("startup")
    async def startup():
        await init_cache()  # Defaults to Redis or in-memory fallback

    @app.on_event("shutdown")
    async def shutdown():
        await close_cache()

    # Using cache decorator
    from cache import cached

    @cached(ttl=3600, key_prefix="document")
    async def parse_document(file_hash: str):
        # Expensive operation
        return result

Custom Backend:
    # Use Supabase or other cache service
    from cache import init_cache, CacheBackend

    class SupabaseCache(CacheBackend):
        async def get(self, key: str): ...
        async def set(self, key: str, value: str, ttl: int): ...
        # ... implement other methods

    await init_cache(SupabaseCache())

In-Memory Testing:
    from cache import init_cache, MemoryBackend

    await init_cache(MemoryBackend())
"""

from .base import CacheBackend
from .redis_backend import RedisBackend
from .memory_backend import MemoryBackend
from .manager import (
    CacheManager,
    cache_manager,
    init_cache,
    close_cache,
    get_cache,
)
from .decorator import cached
from .decorators import (
    cached as cached_advanced,
    cache_by_file_hash,
    CacheConfig,
    invalidate_cache,
)
from .keys import CacheKeyGenerator

__all__ = [
    # Base interface
    "CacheBackend",
    # Backend implementations
    "RedisBackend",
    "MemoryBackend",
    # Cache manager
    "CacheManager",
    "cache_manager",
    "init_cache",
    "close_cache",
    "get_cache",
    # Decorators
    "cached",  # Original simple decorator
    "cached_advanced",  # Advanced decorator with more features
    "cache_by_file_hash",  # File-hash-based caching
    "CacheConfig",  # TTL configurations
    "invalidate_cache",  # Cache invalidation
    # Utilities
    "CacheKeyGenerator",
]
