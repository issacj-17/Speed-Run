# Cache Layer - Usage Guide

## Overview

The cache layer provides a flexible, dependency-injection-based caching system that supports multiple backends (Redis, in-memory, custom). This allows easy swapping between cache services without changing application code.

## Architecture

### SOLID Principles Applied

- **Single Responsibility**: Each component has one clear purpose
- **Open/Closed**: Easy to extend with new backends without modifying existing code
- **Liskov Substitution**: All backends implement `CacheBackend` and are interchangeable
- **Interface Segregation**: `CacheBackend` has a focused interface
- **Dependency Inversion**: Services depend on abstractions, not concrete implementations

### Components

```
cache/
├── base.py                 # Abstract CacheBackend interface
├── redis_backend.py        # Redis implementation
├── memory_backend.py       # In-memory fallback
├── manager.py              # DI-based cache manager
├── decorator.py            # @cached decorator
├── keys.py                 # Cache key utilities
└── __init__.py             # Public API
```

## Quick Start

### 1. Initialize Cache (in main.py)

```python
from fastapi import FastAPI
from cache import init_cache, close_cache

@app.on_event("startup")
async def startup():
    await init_cache()  # Defaults to Redis with in-memory fallback

@app.on_event("shutdown")
async def shutdown():
    await close_cache()
```

### 2. Use Cache Decorator

```python
from cache import cached

@cached(ttl=3600, key_prefix="document")
async def parse_document(file_hash: str):
    """This function's results will be cached for 1 hour."""
    # Expensive operation
    result = await expensive_parsing(file_hash)
    return result
```

### 3. Manual Cache Operations

```python
from cache import cache_manager, CacheKeyGenerator

# Store in cache
key = CacheKeyGenerator.document_parse(file_hash)
await cache_manager.set(key, json.dumps(result), ttl=3600)

# Retrieve from cache
cached_data = await cache_manager.get(key)
if cached_data:
    result = json.loads(cached_data)

# Delete from cache
await cache_manager.delete(key)
```

## Custom Cache Backends

### Using In-Memory Cache (Testing)

```python
from cache import init_cache, MemoryBackend

# In test setup
await init_cache(MemoryBackend())
```

### Using Custom Backend (e.g., Supabase)

```python
from cache import init_cache, CacheBackend

class SupabaseCache(CacheBackend):
    """Custom Supabase cache implementation."""

    async def get(self, key: str) -> Optional[str]:
        # Implement Supabase get
        ...

    async def set(self, key: str, value: str, ttl: int) -> bool:
        # Implement Supabase set
        ...

    async def delete(self, key: str) -> bool:
        # Implement Supabase delete
        ...

    async def exists(self, key: str) -> bool:
        # Implement Supabase exists
        ...

    async def ping(self) -> bool:
        # Health check
        ...

    async def close(self) -> None:
        # Cleanup
        ...

# Use it
await init_cache(SupabaseCache())
```

### Using Memcached

```python
from cache import CacheBackend
import aiomemcache

class MemcachedBackend(CacheBackend):
    def __init__(self, host: str = "localhost", port: int = 11211):
        self._client = None
        self.host = host
        self.port = port

    async def connect(self):
        self._client = await aiomemcache.Client(self.host, self.port)

    async def get(self, key: str) -> Optional[str]:
        return await self._client.get(key.encode())

    async def set(self, key: str, value: str, ttl: int) -> bool:
        await self._client.set(key.encode(), value.encode(), exptime=ttl)
        return True

    # ... implement other methods

# Use it
await init_cache(MemcachedBackend())
```

## Cache Key Generation

Use `CacheKeyGenerator` for consistent key naming:

```python
from cache import CacheKeyGenerator

# Document parsing
key = CacheKeyGenerator.document_parse(file_hash)
# Result: "document:parse:abc123..."

# OCR extraction
key = CacheKeyGenerator.ocr_extract(image_hash)
# Result: "ocr:extract:def456..."

# Image analysis
key = CacheKeyGenerator.image_analysis(image_hash, "tampering")
# Result: "image:tampering:ghi789..."

# Validation
key = CacheKeyGenerator.validation(document_hash, "format")
# Result: "validation:format:jkl012..."

# Risk scores
key = CacheKeyGenerator.risk_score("DOCUMENT", document_id)
# Result: "risk:DOCUMENT:uuid"
```

## Configuration

Set cache behavior in `backend/src/backend/config.py` or `.env`:

```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5

# Cache behavior
CACHE_ENABLED=True
CACHE_DEFAULT_TTL=3600

# TTLs for specific operations
CACHE_TTL_DOCUMENT_PARSING=86400   # 24 hours
CACHE_TTL_OCR=172800                # 48 hours
CACHE_TTL_IMAGE_ANALYSIS=86400      # 24 hours
CACHE_TTL_VALIDATION=43200          # 12 hours
```

## Health Checks

Check cache health in health endpoints:

```python
from cache import cache_manager

@app.get("/health")
async def health():
    cache_healthy = await cache_manager.health_check()
    return {
        "cache": "connected" if cache_healthy else "disconnected"
    }
```

## Testing

### Unit Testing with In-Memory Cache

```python
import pytest
from cache import init_cache, MemoryBackend

@pytest.fixture
async def cache():
    """Provide in-memory cache for tests."""
    await init_cache(MemoryBackend())
    yield
    await close_cache()

@pytest.mark.asyncio
async def test_caching(cache):
    @cached(ttl=60, key_prefix="test")
    async def expensive_function(x: int):
        return x * 2

    # First call - cache miss
    result1 = await expensive_function(5)
    assert result1 == 10

    # Second call - cache hit
    result2 = await expensive_function(5)
    assert result2 == 10
```

### Mocking Cache in Tests

```python
from unittest.mock import AsyncMock
from cache import CacheManager, CacheBackend

@pytest.fixture
async def mock_cache():
    """Provide mocked cache for tests."""
    mock_backend = AsyncMock(spec=CacheBackend)
    mock_backend.get.return_value = None
    mock_backend.set.return_value = True

    manager = CacheManager(mock_backend)
    await manager.init()
    return manager
```

## Fallback Strategy

The cache layer implements graceful degradation:

1. **Primary**: Redis (production)
2. **Fallback**: In-memory cache (if Redis unavailable)
3. **Degraded**: App continues without cache if both fail

```python
# Automatic fallback
await init_cache()  # Tries Redis, falls back to memory

# The decorator handles failures gracefully
@cached(ttl=3600)
async def my_function():
    # If cache is unavailable, function executes normally
    ...
```

## Best Practices

### 1. Choose Appropriate TTLs

```python
# Expensive, rarely changing data: Long TTL
@cached(ttl=86400, key_prefix="document")
async def parse_document(file_hash: str):
    ...

# Frequently changing data: Short TTL
@cached(ttl=300, key_prefix="stats")
async def get_statistics():
    ...
```

### 2. Use File Hashes for Keys

```python
from cache import CacheKeyGenerator

# Compute hash of file content
file_hash = CacheKeyGenerator.compute_hash(file_content)

# Use hash in cache key (content-addressable caching)
key = CacheKeyGenerator.document_parse(file_hash)
```

### 3. Cache Serializable Data

```python
import json

# Good: Simple data types
@cached(ttl=3600)
async def get_config() -> dict:
    return {"key": "value"}

# Bad: Complex objects (won't serialize)
# @cached(ttl=3600)
# async def get_model():
#     return ComplexModelObject()

# Solution: Serialize manually
async def get_model():
    key = "model:latest"
    cached = await cache_manager.get(key)
    if cached:
        return Model.from_dict(json.loads(cached))

    model = await load_model()
    await cache_manager.set(key, json.dumps(model.to_dict()), 3600)
    return model
```

### 4. Invalidate Stale Cache

```python
from cache import cache_manager, CacheKeyGenerator

async def update_document(document_id: str, new_content: bytes):
    # Update document
    await save_document(document_id, new_content)

    # Invalidate cache
    file_hash = CacheKeyGenerator.compute_hash(new_content)
    await cache_manager.delete(CacheKeyGenerator.document_parse(file_hash))
```

## Monitoring

### Cache Hit Rate

```python
import logging

logger = logging.getLogger(__name__)

# The decorator logs cache hits/misses at DEBUG level
# Enable DEBUG logging to monitor cache performance:
# logging.basicConfig(level=logging.DEBUG)

# You'll see:
# DEBUG:cache.decorator:Cache hit: document:parse:abc123
# DEBUG:cache.decorator:Cache miss: document:parse:def456
```

### Redis Monitoring

```bash
# Connect to Redis CLI
docker exec -it speedrun-redis redis-cli

# Check cache statistics
INFO stats

# List all keys
KEYS *

# Check specific key
GET "document:parse:abc123"

# Check key TTL
TTL "document:parse:abc123"
```

## Troubleshooting

### Cache Not Working

1. **Check Redis connection**:
   ```bash
   docker exec -it speedrun-redis redis-cli ping
   ```

2. **Check cache initialization**:
   ```python
   from cache import cache_manager
   healthy = await cache_manager.health_check()
   print(f"Cache healthy: {healthy}")
   ```

3. **Check environment variables**:
   ```bash
   echo $REDIS_URL
   echo $CACHE_ENABLED
   ```

### Cache Growing Too Large

```bash
# Check Redis memory usage
docker exec -it speedrun-redis redis-cli INFO memory

# Redis is configured with LRU eviction:
# maxmemory 2gb
# maxmemory-policy allkeys-lru
```

### Debugging Cache Issues

```python
import logging

# Enable DEBUG logging for cache module
logging.getLogger("cache").setLevel(logging.DEBUG)

# You'll see detailed logs:
# - Cache hits/misses
# - Connection errors
# - Serialization issues
```

## Migration Guide

### From No Cache to Cache

```python
# Before
async def parse_document(file_hash: str):
    result = await docling_parse(file_hash)
    return result

# After
from cache import cached

@cached(ttl=86400, key_prefix="document")
async def parse_document(file_hash: str):
    result = await docling_parse(file_hash)
    return result

# That's it! No other changes needed.
```

### From Redis to Another Backend

```python
# Before (main.py)
await init_cache()  # Uses Redis

# After (main.py)
from cache import init_cache, MemoryBackend
await init_cache(MemoryBackend())

# Or custom backend
await init_cache(SupabaseCache())

# No changes needed in services - they use the same interface!
```

---

**Created:** 2025-01-15
**Status:** Production Ready
**Maintainer:** Speed-Run Team
