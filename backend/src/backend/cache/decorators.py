"""
Caching decorators for expensive operations.

Provides decorators to cache results of expensive operations like document parsing,
NLP analysis, and image processing.
"""

import asyncio
import hashlib
import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Union

from backend.logging import get_logger

logger = get_logger(__name__)


class CacheConfig:
    """Cache TTL configurations for different operation types."""

    # Document parsing (expensive, rarely changes)
    DOCUMENT_PARSE_TTL = 3600  # 1 hour

    # NLP analysis (expensive, deterministic)
    NLP_ANALYSIS_TTL = 1800  # 30 minutes

    # Image processing (fast, rarely changes)
    IMAGE_METADATA_TTL = 3600  # 1 hour

    # Forensic analysis (very expensive)
    FORENSIC_ANALYSIS_TTL = 7200  # 2 hours

    # Validation results (moderate)
    VALIDATION_TTL = 1800  # 30 minutes

    # Default fallback
    DEFAULT_TTL = 600  # 10 minutes


def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        prefix: Key prefix (usually function name)
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Convert Path objects to strings
    processed_args = []
    for arg in args:
        if isinstance(arg, Path):
            processed_args.append(str(arg))
        elif isinstance(arg, bytes):
            # Hash bytes (e.g., file contents)
            processed_args.append(hashlib.md5(arg).hexdigest())
        else:
            processed_args.append(str(arg))

    # Process kwargs
    processed_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, Path):
            processed_kwargs[k] = str(v)
        elif isinstance(v, bytes):
            processed_kwargs[k] = hashlib.md5(v).hexdigest()
        else:
            processed_kwargs[k] = str(v)

    # Create stable string representation
    key_parts = [prefix] + processed_args
    if processed_kwargs:
        sorted_kwargs = sorted(processed_kwargs.items())
        key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))

    key_string = ":".join(key_parts)

    # Hash the key to keep it a reasonable length
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()

    return f"{prefix}:{key_hash}"


def cached(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    cache_none: bool = False,
):
    """
    Decorator to cache async function results.

    Args:
        ttl: Time-to-live in seconds (None = use default)
        key_prefix: Custom key prefix (None = use function name)
        cache_none: Whether to cache None results

    Returns:
        Decorated function with caching

    Example:
        @cached(ttl=3600, key_prefix="doc_parse")
        async def parse_document(file_path: Path):
            # Expensive operation
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache manager
            try:
                from backend.cache import get_cache

                cache = await get_cache()
            except Exception as e:
                logger.warning("cache_unavailable", error=str(e))
                # Execute without caching if cache unavailable
                return await func(*args, **kwargs)

            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = _generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            try:
                cached_result = await cache.get(cache_key)
                if cached_result is not None:
                    logger.debug("cache_hit", key=cache_key, function=func.__name__)
                    # Deserialize result
                    import pickle

                    result = pickle.loads(cached_result.encode("latin1"))
                    return result
            except Exception as e:
                logger.warning("cache_get_failed", key=cache_key, error=str(e))

            # Cache miss - execute function
            logger.debug("cache_miss", key=cache_key, function=func.__name__)
            result = await func(*args, **kwargs)

            # Cache the result
            if result is not None or cache_none:
                try:
                    import pickle

                    serialized = pickle.dumps(result).decode("latin1")
                    actual_ttl = ttl or CacheConfig.DEFAULT_TTL
                    await cache.set(cache_key, serialized, ttl=actual_ttl)
                    logger.debug(
                        "cache_set",
                        key=cache_key,
                        function=func.__name__,
                        ttl=actual_ttl,
                    )
                except Exception as e:
                    logger.warning("cache_set_failed", key=cache_key, error=str(e))

            return result

        return wrapper

    return decorator


def cache_by_file_hash(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    file_arg_index: int = 0,
):
    """
    Decorator to cache results based on file content hash.

    More reliable than caching by file path, as it detects file changes.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Custom key prefix
        file_arg_index: Index of file path argument (default: 0, first arg)

    Returns:
        Decorated function with file-hash-based caching

    Example:
        @cache_by_file_hash(ttl=3600, key_prefix="doc_parse")
        async def parse_document(file_path: Path):
            # Expensive operation
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache manager
            try:
                from backend.cache import get_cache

                cache = await get_cache()
            except Exception as e:
                logger.warning("cache_unavailable", error=str(e))
                return await func(*args, **kwargs)

            # Extract file path
            if len(args) > file_arg_index:
                file_path = args[file_arg_index]
            else:
                # File path might be in kwargs
                file_path = kwargs.get("file_path") or kwargs.get("path")

            if not file_path or not isinstance(file_path, Path):
                logger.warning(
                    "cache_by_file_hash_no_path",
                    function=func.__name__,
                    msg="File path not found, executing without cache",
                )
                return await func(*args, **kwargs)

            # Calculate file hash
            try:
                file_hash = await asyncio.to_thread(_calculate_file_hash, file_path)
            except Exception as e:
                logger.warning("file_hash_failed", file_path=str(file_path), error=str(e))
                return await func(*args, **kwargs)

            # Generate cache key with file hash
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = f"{prefix}:file:{file_hash}"

            # Try to get from cache
            try:
                cached_result = await cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(
                        "cache_hit",
                        key=cache_key,
                        function=func.__name__,
                        file=file_path.name,
                    )
                    import pickle

                    result = pickle.loads(cached_result.encode("latin1"))
                    return result
            except Exception as e:
                logger.warning("cache_get_failed", key=cache_key, error=str(e))

            # Cache miss - execute function
            logger.debug(
                "cache_miss", key=cache_key, function=func.__name__, file=file_path.name
            )
            result = await func(*args, **kwargs)

            # Cache the result
            if result is not None:
                try:
                    import pickle

                    serialized = pickle.dumps(result).decode("latin1")
                    actual_ttl = ttl or CacheConfig.DEFAULT_TTL
                    await cache.set(cache_key, serialized, ttl=actual_ttl)
                    logger.debug(
                        "cache_set",
                        key=cache_key,
                        function=func.__name__,
                        ttl=actual_ttl,
                        file=file_path.name,
                    )
                except Exception as e:
                    logger.warning("cache_set_failed", key=cache_key, error=str(e))

            return result

        return wrapper

    return decorator


def _calculate_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of file contents."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read in chunks for memory efficiency
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def invalidate_cache(key_pattern: str) -> None:
    """
    Invalidate cache entries matching a pattern.

    Args:
        key_pattern: Cache key pattern to invalidate

    Note: This is a placeholder. Actual implementation depends on cache backend.
    Redis supports pattern-based deletion, in-memory cache can implement similar.
    """
    logger.info("cache_invalidate_requested", pattern=key_pattern)
    # TODO: Implement pattern-based cache invalidation
    pass


__all__ = [
    "cached",
    "cache_by_file_hash",
    "CacheConfig",
    "invalidate_cache",
]
