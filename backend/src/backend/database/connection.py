"""
Database connection management for PostgreSQL.

Provides:
- Async SQLAlchemy engine with connection pooling
- Database initialization
- Health check utilities
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool

from ..config import settings

logger = logging.getLogger(__name__)

# Global engine instance
engine: AsyncEngine | None = None


def create_engine() -> AsyncEngine:
    """
    Create async SQLAlchemy engine with connection pooling.

    Configuration from settings:
    - DATABASE_URL: PostgreSQL connection string
    - DB_POOL_SIZE: Connection pool size (default: 20)
    - DB_MAX_OVERFLOW: Max overflow connections (default: 10)
    - DB_ECHO: Echo SQL statements (default: False)

    Returns:
        AsyncEngine: Configured async engine
    """
    # Determine pool class
    if settings.TESTING:
        # Use NullPool for testing (no connection reuse)
        pool_class = NullPool
        pool_kwargs = {}
    else:
        # Use QueuePool for production (connection pooling)
        pool_class = QueuePool
        pool_kwargs = {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_pre_ping": True,  # Test connections before using
            "pool_recycle": 3600,   # Recycle connections after 1 hour
        }

    # Create engine
    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        future=True,
        poolclass=pool_class,
        **pool_kwargs,
    )

    logger.info(
        "Database engine created",
        extra={
            "database_url": settings.DATABASE_URL.split("@")[-1],  # Hide credentials
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
        },
    )

    return _engine


async def init_db() -> None:
    """
    Initialize database connection.

    Should be called on application startup.
    """
    global engine

    if engine is None:
        engine = create_engine()
        logger.info("Database initialized")
    else:
        logger.warning("Database already initialized")


async def close_db() -> None:
    """
    Close database connection.

    Should be called on application shutdown.
    """
    global engine

    if engine is not None:
        await engine.dispose()
        engine = None
        logger.info("Database connection closed")
    else:
        logger.warning("Database not initialized")


async def check_db_health() -> bool:
    """
    Check database connection health.

    Returns:
        bool: True if database is healthy, False otherwise
    """
    global engine

    if engine is None:
        logger.error("Database not initialized")
        return False

    try:
        # Try to execute a simple query
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database health check passed")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def get_db() -> AsyncGenerator:
    """
    Dependency for FastAPI to get database session.

    Usage:
        @app.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session
    """
    from .session import async_session_maker

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Export
__all__ = [
    "engine",
    "create_engine",
    "init_db",
    "close_db",
    "check_db_health",
    "get_db",
]
