"""
FastAPI dependency injection helpers.

Provides reusable dependencies for routes using FastAPI's Depends() system.
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_session
from backend.services.alert_service import AlertService
from backend.services.corroboration_service import CorroborationService
from backend.container import get_container, Container
from backend.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# Database Dependencies
# ============================================================================


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide database session for request.

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session
    """
    async for session in get_session():
        try:
            yield session
        except Exception as e:
            logger.error("database_session_error", error=str(e))
            raise


# ============================================================================
# Service Dependencies
# ============================================================================


def get_container_dependency() -> Container:
    """
    Provide dependency injection container.

    Usage:
        def get_my_service(container: Container = Depends(get_container_dependency)):
            return MyService(container.document_parser, container.nlp_processor)

    Returns:
        Container: DI container with configured adapters
    """
    return get_container()


def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    """
    Provide AlertService with database session.

    Usage:
        @app.get("/alerts")
        async def list_alerts(alert_service: AlertService = Depends(get_alert_service)):
            return await alert_service.list_alerts()

    Args:
        db: Database session (injected)

    Returns:
        AlertService: Alert management service
    """
    return AlertService(db)


def get_corroboration_service(
    container: Container = Depends(get_container_dependency),
) -> CorroborationService:
    """
    Provide CorroborationService with DI container dependencies.

    Usage:
        @app.post("/corroborate")
        async def corroborate(
            service: CorroborationService = Depends(get_corroboration_service)
        ):
            return await service.analyze_document(...)

    Args:
        container: DI container (injected)

    Returns:
        CorroborationService: Document corroboration service
    """
    return CorroborationService(
        document_parser=container.document_parser,
        nlp_processor=container.nlp_processor,
        image_processor=container.image_processor,
    )


# ============================================================================
# Authentication & Authorization Dependencies (Placeholder)
# ============================================================================


async def get_current_user(
    # token: str = Depends(oauth2_scheme)  # Future: Add OAuth2 scheme
) -> dict:
    """
    Get current authenticated user.

    Placeholder for future authentication implementation.

    Usage:
        @app.get("/me")
        async def read_current_user(user: dict = Depends(get_current_user)):
            return user

    Returns:
        dict: Current user information

    Raises:
        HTTPException: If authentication fails
    """
    # TODO: Implement actual authentication
    # For now, return a mock user for development
    logger.warning("using_mock_authentication", msg="Implement real auth before production")

    return {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "username": "dev_user",
        "roles": ["admin"],
    }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get current active user (not disabled/suspended).

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_active_user)):
            return user

    Args:
        current_user: Current user (injected)

    Returns:
        dict: Active user information

    Raises:
        HTTPException: If user is not active
    """
    # TODO: Check if user is active in database
    if current_user.get("disabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return current_user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.

    Usage:
        @app.delete("/alerts/{alert_id}")
        async def delete_alert(
            alert_id: UUID,
            user: dict = Depends(require_role("admin"))
        ):
            ...

    Args:
        required_role: Required role name

    Returns:
        Dependency function that checks role

    Raises:
        HTTPException: If user doesn't have required role
    """

    async def check_role(user: dict = Depends(get_current_active_user)) -> dict:
        user_roles = user.get("roles", [])
        if required_role not in user_roles:
            logger.warning(
                "access_denied_insufficient_role",
                user_id=user.get("user_id"),
                required_role=required_role,
                user_roles=user_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        return user

    return check_role


# ============================================================================
# Pagination Dependencies
# ============================================================================


def pagination_params(
    skip: int = 0,
    limit: int = 100,
) -> dict:
    """
    Standard pagination parameters.

    Usage:
        @app.get("/items")
        async def list_items(pagination: dict = Depends(pagination_params)):
            skip = pagination["skip"]
            limit = pagination["limit"]
            ...

    Args:
        skip: Number of items to skip (default: 0)
        limit: Max items to return (default: 100, max: 1000)

    Returns:
        dict: Pagination parameters
    """
    # Enforce maximum limit
    if limit > 1000:
        limit = 1000

    return {"skip": skip, "limit": limit}


__all__ = [
    # Database
    "get_db",
    # Services
    "get_container_dependency",
    "get_alert_service",
    "get_corroboration_service",
    # Authentication
    "get_current_user",
    "get_current_active_user",
    "require_role",
    # Utilities
    "pagination_params",
]
