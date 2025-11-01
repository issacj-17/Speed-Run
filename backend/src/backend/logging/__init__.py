"""
Structured logging infrastructure for Speed-Run AML Platform.

Provides JSON-formatted logs, audit trails, and correlation IDs.

Quick Start:
    # Configure logging (in main.py startup)
    from logging import configure_logging

    configure_logging(level="INFO", json_output=True)

    # Use logger in services
    from logging import get_logger

    logger = get_logger(__name__)
    logger.info("operation_completed", user_id=123, duration_ms=45)

    # Audit logging
    from logging import audit_logger

    await audit_logger.log(
        event_type="document_uploaded",
        entity_type="DOCUMENT",
        entity_id=doc_id,
        user_id=user.id,
        action="UPLOAD",
    )

    # Add middleware (in main.py)
    from logging import LoggingMiddleware

    app.add_middleware(LoggingMiddleware)
"""

from .config import configure_logging, get_logger
from .audit import AuditLogger, audit_logger
from .context import (
    get_correlation_id,
    set_correlation_id,
    get_request_id,
    set_request_id,
    get_user_id,
    set_user_id,
    clear_context,
)
from .middleware import LoggingMiddleware

__all__ = [
    # Configuration
    "configure_logging",
    "get_logger",
    # Audit logging
    "AuditLogger",
    "audit_logger",
    # Context management
    "get_correlation_id",
    "set_correlation_id",
    "get_request_id",
    "set_request_id",
    "get_user_id",
    "set_user_id",
    "clear_context",
    # Middleware
    "LoggingMiddleware",
]
