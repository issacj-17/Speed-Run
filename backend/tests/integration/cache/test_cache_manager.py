"""
Integration tests for CacheManager.

Tests cache manager with actual backends (no mocking).
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.cache.manager import CacheManager, init_cache, close_cache
from backend.cache.memory_backend import MemoryBackend
from backend.cache.base import CacheBackend


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_initializes_with_memory_backend():
    """Test CacheManager initializes with memory backend."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)

    # Act
    await manager.init()

    # Assert
    assert manager._initialized is True
    assert manager._backend is backend

    # Cleanup
    await manager.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_raises_error_when_accessing_backend_before_init():
    """Test accessing backend before init raises RuntimeError."""
    # Arrange
    manager = CacheManager()

    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        _ = manager.backend

    assert "not initialized" in str(exc_info.value).lower()


@pytest.mark.integration
@pytest.mark.asyncio
@patch("backend.config.settings")
async def test_cache_manager_defaults_to_memory_when_cache_disabled(mock_settings):
    """Test CacheManager uses memory backend when caching is disabled."""
    # Arrange
    mock_settings.CACHE_ENABLED = False
    manager = CacheManager()

    # Act
    await manager.init()

    # Assert
    assert isinstance(manager._backend, MemoryBackend)

    # Cleanup
    await manager.close()


# ============================================================================
# Basic Operations Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_set_and_get():
    """Test CacheManager set and get operations."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)
    await manager.init()

    # Act
    await manager.set("test_key", "test_value", ttl=60)
    result = await manager.get("test_key")

    # Assert
    assert result == "test_value"

    # Cleanup
    await manager.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_delete():
    """Test CacheManager delete operation."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)
    await manager.init()
    await manager.set("test_key", "test_value", ttl=60)

    # Act
    success = await manager.delete("test_key")
    result = await manager.get("test_key")

    # Assert
    assert success is True
    assert result is None

    # Cleanup
    await manager.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_exists():
    """Test CacheManager exists operation."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)
    await manager.init()
    await manager.set("test_key", "test_value", ttl=60)

    # Act
    exists = await manager.exists("test_key")
    not_exists = await manager.exists("nonexistent_key")

    # Assert
    assert exists is True
    assert not_exists is False

    # Cleanup
    await manager.close()


# ============================================================================
# Health Check Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_health_check_returns_true_when_healthy():
    """Test health_check returns True for healthy backend."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)
    await manager.init()

    # Act
    healthy = await manager.health_check()

    # Assert
    assert healthy is True

    # Cleanup
    await manager.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_health_check_returns_false_before_init():
    """Test health_check returns False before initialization."""
    # Arrange
    manager = CacheManager()

    # Act
    healthy = await manager.health_check()

    # Assert
    assert healthy is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_health_check_returns_false_after_close():
    """Test health_check returns False after closing."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)
    await manager.init()
    await manager.close()

    # Act
    healthy = await manager.health_check()

    # Assert
    assert healthy is False


# ============================================================================
# Close Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_close_closes_backend():
    """Test close properly closes the backend."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)
    await manager.init()

    # Act
    await manager.close()

    # Assert
    assert manager._initialized is False
    assert len(backend._cache) == 0


# ============================================================================
# Global Functions Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_init_cache_with_custom_backend():
    """Test init_cache function with custom backend."""
    # Arrange
    backend = MemoryBackend()

    # Act
    manager = await init_cache(backend=backend)

    # Assert
    assert manager._backend is backend
    assert manager._initialized is True

    # Cleanup
    await close_cache()


@pytest.mark.integration
@pytest.mark.asyncio
@patch("backend.config.settings")
async def test_init_cache_without_backend_uses_default(mock_settings):
    """Test init_cache without backend uses default."""
    # Arrange
    mock_settings.CACHE_ENABLED = False

    # Act
    manager = await init_cache()

    # Assert
    assert isinstance(manager._backend, MemoryBackend)
    assert manager._initialized is True

    # Cleanup
    await close_cache()


# ============================================================================
# Backend Property Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_backend_property_returns_backend():
    """Test backend property returns the backend instance."""
    # Arrange
    backend = MemoryBackend()
    manager = CacheManager(backend=backend)
    await manager.init()

    # Act
    retrieved_backend = manager.backend

    # Assert
    assert retrieved_backend is backend

    # Cleanup
    await manager.close()


# ============================================================================
# Integration with Custom Backend Tests
# ============================================================================


class MockCacheBackend(CacheBackend):
    """Mock backend for testing custom backend integration."""

    def __init__(self):
        self.connected = False
        self.storage = {}

    async def connect(self):
        self.connected = True

    async def get(self, key: str):
        return self.storage.get(key)

    async def set(self, key: str, value: str, ttl: int):
        self.storage[key] = value
        return True

    async def delete(self, key: str):
        if key in self.storage:
            del self.storage[key]
            return True
        return False

    async def exists(self, key: str):
        return key in self.storage

    async def ping(self):
        return self.connected

    async def close(self):
        self.connected = False
        self.storage.clear()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_works_with_custom_backend():
    """Test CacheManager works with custom backend implementation."""
    # Arrange
    backend = MockCacheBackend()
    manager = CacheManager(backend=backend)
    await manager.init()

    # Act
    await manager.set("test_key", "test_value", ttl=60)
    result = await manager.get("test_key")

    # Assert
    assert result == "test_value"
    assert backend.connected is True

    # Cleanup
    await manager.close()
    assert backend.connected is False


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_manager_handles_backend_connect_failure():
    """Test CacheManager handles backend connection failure gracefully."""
    # Arrange
    class FailingBackend(CacheBackend):
        async def connect(self):
            raise RuntimeError("Connection failed")

        async def get(self, key: str):
            pass

        async def set(self, key: str, value: str, ttl: int):
            pass

        async def delete(self, key: str):
            pass

        async def exists(self, key: str):
            pass

        async def ping(self):
            pass

        async def close(self):
            pass

    backend = FailingBackend()
    manager = CacheManager(backend=backend)

    # Act & Assert
    with pytest.raises(RuntimeError):
        await manager.init()
