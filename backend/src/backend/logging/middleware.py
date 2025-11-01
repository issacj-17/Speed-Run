"""
FastAPI middleware for request/response logging.
"""

import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import structlog

from .context import set_correlation_id, set_request_id, clear_context

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests and responses.

    Adds correlation IDs and logs request/response details.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        request_id = str(uuid4())

        # Set context
        set_correlation_id(correlation_id)
        set_request_id(request_id)

        # Extract user info if available (from auth headers)
        # user_id = request.headers.get("X-User-ID")
        # if user_id:
        #     set_user_id(user_id)

        # Log request
        start_time = time.time()

        logger.info(
            "request_started",
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                "request_completed",
                method=request.method,
                url=str(request.url),
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "request_failed",
                method=request.method,
                url=str(request.url),
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
            )

            raise

        finally:
            # Clear context
            clear_context()


__all__ = ["LoggingMiddleware"]
