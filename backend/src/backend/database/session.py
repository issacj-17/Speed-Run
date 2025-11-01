"""
Database session management.

Provides:
- Async session factory
- Session context managers
- Session utilities
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .connection import engine

logger = logging.getLogger(__name__)

# Session factory
async_session_maker: async_sessionmaker[AsyncSession] | None = None


def create_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Create async session factory.

    Returns:
        async_sessionmaker: Session factory
    """
    if engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")

    factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Don't expire objects after commit
        autocommit=False,
        autoflush=False,
    )

    logger.info("Session factory created")
    return factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session as async generator.

    Usage:
        async with get_session() as session:
            result = await session.execute(query)

    Yields:
        AsyncSession: Database session
    """
    global async_session_maker

    if async_session_maker is None:
        async_session_maker = create_session_factory()

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide transactional scope for database operations.

    Usage:
        async with session_scope() as session:
            user = await session.get(User, user_id)
            user.name = "New Name"
            # Automatic commit on exit, rollback on exception

    Yields:
        AsyncSession: Database session with automatic commit/rollback
    """
    global async_session_maker

    if async_session_maker is None:
        async_session_maker = create_session_factory()

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("Session committed")
        except Exception as e:
            await session.rollback()
            logger.error(f"Session rolled back due to error: {e}")
            raise
        finally:
            await session.close()
            logger.debug("Session closed")


# Initialize session factory on import
def init_session_factory():
    """Initialize session factory if engine is available."""
    global async_session_maker

    if engine is not None and async_session_maker is None:
        async_session_maker = create_session_factory()


# Export
__all__ = [
    "async_session_maker",
    "create_session_factory",
    "get_session",
    "session_scope",
    "init_session_factory",
]
