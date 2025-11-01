"""
Logging context management for correlation IDs and request tracking.
"""

import contextvars
from typing import Optional
from uuid import uuid4

import structlog

# Context variables for request tracking
correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "correlation_id", default=None
)

request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)

user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)


def get_correlation_id() -> str:
    """
    Get current correlation ID or generate new one.

    Returns:
        Correlation ID (UUID)
    """
    correlation_id = correlation_id_var.get()
    if correlation_id is None:
        correlation_id = str(uuid4())
        set_correlation_id(correlation_id)
    return correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for current context.

    Args:
        correlation_id: Correlation ID to set
    """
    correlation_id_var.set(correlation_id)
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def get_request_id() -> Optional[str]:
    """
    Get current request ID.

    Returns:
        Request ID or None
    """
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """
    Set request ID for current context.

    Args:
        request_id: Request ID to set
    """
    request_id_var.set(request_id)
    structlog.contextvars.bind_contextvars(request_id=request_id)


def get_user_id() -> Optional[str]:
    """
    Get current user ID.

    Returns:
        User ID or None
    """
    return user_id_var.get()


def set_user_id(user_id: str) -> None:
    """
    Set user ID for current context.

    Args:
        user_id: User ID to set
    """
    user_id_var.set(user_id)
    structlog.contextvars.bind_contextvars(user_id=user_id)


def clear_context() -> None:
    """Clear all context variables."""
    correlation_id_var.set(None)
    request_id_var.set(None)
    user_id_var.set(None)
    structlog.contextvars.clear_contextvars()


__all__ = [
    "get_correlation_id",
    "set_correlation_id",
    "get_request_id",
    "set_request_id",
    "get_user_id",
    "set_user_id",
    "clear_context",
]
