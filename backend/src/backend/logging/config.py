"""
Structured logging configuration using structlog.

Provides JSON-formatted logs for machine parsing and audit trails.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog
from pythonjsonlogger import jsonlogger

from backend.config import settings


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    json_output: bool = True,
) -> None:
    """
    Configure structured logging with structlog.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, AUDIT)
        log_file: Optional file path for logs
        json_output: Whether to output JSON format (True for production)

    Example:
        configure_logging(level="INFO", json_output=True)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    # Add custom AUDIT level (between WARNING and ERROR)
    AUDIT_LEVEL = 35
    logging.addLevelName(AUDIT_LEVEL, "AUDIT")

    def audit(self, message, *args, **kwargs):
        if self.isEnabledFor(AUDIT_LEVEL):
            self._log(AUDIT_LEVEL, message, args, **kwargs)

    logging.Logger.audit = audit

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add JSON renderer for production, console for development
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure file logging if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        if json_output:
            formatter = jsonlogger.JsonFormatter(
                "%(timestamp)s %(level)s %(name)s %(message)s"
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger

    Example:
        logger = get_logger(__name__)
        logger.info("operation_completed", user_id=123, duration_ms=45)
    """
    return structlog.get_logger(name)


__all__ = ["configure_logging", "get_logger"]
