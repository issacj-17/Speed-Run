"""
Cache decorator for expensive operations.
"""

import functools
import json
import logging
from typing import Any, Callable, Optional

from .manager import cache_manager
from backend.config import settings

logger = logging.getLogger(__name__)


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    enabled: Optional[bool] = None,
):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds (defaults to CACHE_DEFAULT_TTL)
        key_prefix: Prefix for cache key (e.g., "document", "ocr")
        enabled: Whether caching is enabled (defaults to CACHE_ENABLED)

    Usage:
        @cached(ttl=3600, key_prefix="document")
        async def parse_document(file_hash: str):
            # Expensive operation
            return result

    Example with custom cache backend:
        # In your startup code:
        from cache import init_cache
        from cache.redis_backend import RedisBackend

        # Use Redis
        await init_cache(RedisBackend())

        # Or use in-memory for testing
        from cache.memory_backend import MemoryBackend
        await init_cache(MemoryBackend())

        # Or use custom backend (Supabase, etc.)
        class SupabaseCache(CacheBackend):
            ...
        await init_cache(SupabaseCache())
    """
    # Set defaults
    if enabled is None:
        enabled = settings.CACHE_ENABLED
    if ttl is None:
        ttl = settings.CACHE_DEFAULT_TTL

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # If caching disabled, just call function
            if not enabled:
                return await func(*args, **kwargs)

            # Generate cache key from function name and arguments
            key_parts = [key_prefix] if key_prefix else []
            key_parts.append(func.__name__)

            # Add positional args
            for arg in args:
                key_parts.append(str(arg))

            # Add keyword args (sorted for consistency)
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")

            cache_key = ":".join(key_parts)

            # Try to get from cache
            try:
                cached_value = await cache_manager.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Cache read error for key {cache_key}: {e}")

            # Cache miss - compute value
            logger.debug(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            try:
                await cache_manager.set(
                    cache_key,
                    json.dumps(result, default=str),
                    ttl,
                )
                logger.debug(f"Cached result: {cache_key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Cache write error for key {cache_key}: {e}")

            return result

        return wrapper

    return decorator


__all__ = ["cached"]
